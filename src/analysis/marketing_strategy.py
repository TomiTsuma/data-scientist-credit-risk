"""Select target segments and craft Kenya premium loan campaign recommendations."""

from __future__ import annotations

import pandas as pd

PRODUCT_WEIGHTS = {
    "stability": 0.35,
    "affluence": 0.25,
    "growth": 0.15,
    "size": 0.15,
    "low_default": 0.10,
}


def score_segments_for_premium_loan(df: pd.DataFrame, country: str = "Kenya") -> pd.DataFrame:
    """Rank segments for premium loan suitability in a given country."""
    kenya = df[df["country_name"].str.lower() == country.lower()].copy()
    if kenya.empty:
        kenya = df.copy()

    seg = kenya.groupby(["segment_id", "segment_name"]).agg(
        customers=("customer_id", "count"),
        stability=("repayment_progress", "mean"),
        affluence=("financed_amount", "mean"),
        growth=("account_age_days", "mean"),
        default_rate=("is_default", "mean"),
        arrears_rate=("is_in_arrears", "mean"),
        payg_share=("payment_type", lambda s: (s == "PAYG").mean()),
    ).reset_index()

    seg["size_score"] = seg["customers"] / seg["customers"].max()
    seg["stability_score"] = seg["stability"]
    seg["affluence_score"] = seg["affluence"] / seg["affluence"].max()
    seg["growth_score"] = 1 - (seg["growth"] / seg["growth"].max()).clip(0, 1)
    seg["low_default_score"] = 1 - seg["default_rate"]

    seg["campaign_score"] = (
        PRODUCT_WEIGHTS["stability"] * seg["stability_score"]
        + PRODUCT_WEIGHTS["affluence"] * seg["affluence_score"]
        + PRODUCT_WEIGHTS["growth"] * seg["growth_score"]
        + PRODUCT_WEIGHTS["size"] * seg["size_score"]
        + PRODUCT_WEIGHTS["low_default"] * seg["low_default_score"]
        - 0.5 * seg["arrears_rate"]
        - 0.4 * seg["default_rate"]
    )

    return seg.sort_values("campaign_score", ascending=False)


def top_two_segments(df: pd.DataFrame, country: str = "Kenya") -> pd.DataFrame:
    ranked = score_segments_for_premium_loan(df, country=country)
    eligible = ranked[
        (ranked["arrears_rate"] <= 0.15)
        & (ranked["default_rate"] <= 0.10)
        & (ranked["stability"] >= 0.55)
    ]
    if len(eligible) >= 2:
        return eligible.head(2)
    if len(eligible) == 1:
        filler = ranked[~ranked["segment_id"].isin(eligible["segment_id"])].head(1)
        return pd.concat([eligible, filler]).head(2)
    return ranked.head(2)


def campaign_recommendations(segment_row: pd.Series) -> dict[str, str]:
    """Message and channel strategy per segment archetype."""
    name = str(segment_row.get("segment_name", ""))
    if "Stable Premium" in name or "Reliable" in name:
        return {
            "headline": "Grow your farm with flexible premium financing",
            "message": (
                "You have a strong repayment track record with SunCulture. "
                "Unlock a premium loan for upgraded equipment, longer terms, and "
                "priority servicing—built for established PAYG customers ready to scale."
            ),
            "cta": "Apply via your SunCulture agent or dial *XXX#",
            "channels": "Field agent visit (primary), SMS reminder, WhatsApp follow-up",
            "channel_rationale": (
                "High-trust, high-value offer suits assisted sales; digital nudges reinforce "
                "agents who already know the customer."
            ),
        }
    if "Early-Tenure" in name:
        return {
            "headline": "Step up to premium credit as you grow",
            "message": (
                "You've started strong with SunCulture. A premium loan can help you expand "
                "acreage or add irrigation capacity—with rates aligned to your improving profile."
            ),
            "cta": "Talk to your agent about premium eligibility",
            "channels": "SMS + inbound call center + regional demo days",
            "channel_rationale": (
                "Growing customers need education and social proof before committing to premium debt."
            ),
        }
    return {
        "headline": "Premium financing for proven SunCulture customers",
        "message": (
            "Based on your account history, you may qualify for a premium loan with "
            "competitive terms for productive assets in Kenya."
        ),
        "cta": "Contact your agent to check eligibility",
        "channels": "Agent-led outreach + SMS",
        "channel_rationale": "Conservative touch for mixed-risk profiles; human vetting before offer.",
    }
