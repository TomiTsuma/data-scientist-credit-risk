"""
generate_charts.py
------------------
Standalone version of the 02_eda_business_storytelling notebook charts.
Saves all 5 PNGs to the reports/ directory.
Run with:  uv run python scripts/generate_charts.py
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from clickhouse_driver import Client
from pathlib import Path

# ── Connection ────────────────────────────────────────────────────────────────
client = Client(
    host="localhost", port=9000,
    user="clickhouse_user", password="clickhouse_password"
)

Path("reports").mkdir(exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
PALETTE = ["#4361EE", "#F72585", "#7209B7", "#4CC9F0", "#3A0CA3"]
BG      = "#0F1117"
CARD    = "#1A1D27"
TEXT    = "#E8EAED"
ACCENT  = "#4361EE"
WARN    = "#F72585"

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    CARD,
    "axes.edgecolor":    "#2D2F3E",
    "axes.labelcolor":   TEXT,
    "xtick.color":       TEXT,
    "ytick.color":       TEXT,
    "text.color":        TEXT,
    "grid.color":        "#2D2F3E",
    "grid.linewidth":    0.5,
    "axes.grid":         True,
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
})


# ─────────────────────────────────────────────────────────────────────────────
# CHART 1 — QoQ Sales Growth Heatmap
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 1: QoQ Sales Growth...")

qoq_df = pd.DataFrame(
    client.execute("""
        SELECT
            country_name,
            toYear(sale_date)   AS yr,
            toQuarter(sale_date) AS qtr,
            concat(toString(toYear(sale_date)), '-Q',
                   toString(toQuarter(sale_date))) AS period,
            count() AS sales_count
        FROM sunculture_db.mart_sales_performance
        GROUP BY country_name, yr, qtr, period
        ORDER BY country_name, yr, qtr
    """),
    columns=["country", "yr", "qtr", "period", "sales"]
)
qoq_df = qoq_df.sort_values(["country", "yr", "qtr"])
qoq_df["qoq_pct"] = qoq_df.groupby("country")["sales"].pct_change() * 100
qoq_df = qoq_df.dropna(subset=["qoq_pct"])
pivot  = qoq_df.pivot(index="country", columns="period", values="qoq_pct")

fig, ax = plt.subplots(figsize=(14, 4))
fig.suptitle("Quarter-over-Quarter Sales Growth Rate (%)", fontsize=15, fontweight="bold", y=1.02)
sns.heatmap(
    pivot, ax=ax, cmap="RdYlGn", center=0,
    annot=True, fmt=".1f", annot_kws={"size": 10},
    linewidths=0.5, linecolor="#0F1117",
    cbar_kws={"label": "QoQ Growth (%)"},
)
ax.set_xlabel("Quarter")
ax.set_ylabel("Country")
ax.tick_params(axis="x", rotation=30)
plt.tight_layout()
plt.savefig("reports/01_qoq_sales_growth.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  ✓ reports/01_qoq_sales_growth.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 2 — Monthly Sales Trend
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 2: Monthly Sales Trend...")

mdf = pd.DataFrame(
    client.execute("""
        SELECT
            country_name,
            toStartOfMonth(sale_date) AS month,
            count() AS sales_count
        FROM sunculture_db.mart_sales_performance
        GROUP BY country_name, month
        ORDER BY country_name, month
    """),
    columns=["country", "month", "sales"]
)
mdf["month"] = pd.to_datetime(mdf["month"])
countries    = sorted(mdf["country"].unique())
colors_map   = dict(zip(countries, PALETTE[:len(countries)]))

fig, ax = plt.subplots(figsize=(14, 5))
for country, grp in mdf.groupby("country"):
    grp = grp.sort_values("month")
    ax.plot(grp["month"], grp["sales"], marker="o", ms=4,
            label=country, color=colors_map[country], linewidth=2)
    rolling = grp.set_index("month")["sales"].rolling(3, min_periods=1).mean()
    ax.plot(rolling.index, rolling.values, "--", alpha=0.45,
            color=colors_map[country], linewidth=1.2)

ax.set_title("Monthly Sales Volume by Country  (dashed = 3-month rolling avg)", pad=10)
ax.set_xlabel("Month")
ax.set_ylabel("Sales Count")
ax.legend(framealpha=0.15, loc="upper left")
ax.xaxis.set_major_locator(mticker.MaxNLocator(10))
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("reports/02_monthly_sales_trend.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  ✓ reports/02_monthly_sales_trend.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 3 — Installation Delay Distribution
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 3: Installation Delay Distribution...")

ddf = pd.DataFrame(
    client.execute("""
        SELECT country_name, installation_delay_days, installation_status
        FROM sunculture_db.mart_installation_operations
        WHERE installation_delay_days BETWEEN -30 AND 90
    """),
    columns=["country", "delay_days", "status"]
)
country_list = sorted(ddf["country"].unique())
fig, axes = plt.subplots(1, len(country_list), figsize=(14, 4), sharey=False)
if len(country_list) == 1:
    axes = [axes]
fig.suptitle(
    "Installation Delay Distribution by Country\n(negative = install before sale — data quality flag)",
    fontsize=13, fontweight="bold"
)
for i, (country, ax) in enumerate(zip(country_list, axes)):
    subset = ddf[ddf["country"] == country]["delay_days"]
    color  = PALETTE[i % len(PALETTE)]
    ax.hist(subset, bins=30, color=color, alpha=0.85, edgecolor="#0F1117", linewidth=0.4)
    ax.axvline(0, color=WARN, linewidth=1.5, linestyle="--", label="Sale date")
    ax.axvline(subset.median(), color="#4CC9F0", linewidth=1.5, linestyle=":",
               label=f"Median {subset.median():.0f}d")
    ax.set_title(country)
    ax.set_xlabel("Days")
    if i == 0:
        ax.set_ylabel("Count")
    ax.legend(fontsize=8, framealpha=0.15)
plt.tight_layout()
plt.savefig("reports/03_installation_delay_dist.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  ✓ reports/03_installation_delay_dist.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 4 — Arrears Rate by Country & Product Tier
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 4: Arrears Rate by Country & Product Tier...")

adf = pd.DataFrame(
    client.execute("""
        SELECT
            country_name,
            product_tier,
            countIf(is_in_arrears = true)  AS in_arrears,
            count()                        AS total,
            round(countIf(is_in_arrears = true) / count() * 100, 1) AS arrears_pct
        FROM sunculture_db.mart_customer_account_analytics
        GROUP BY country_name, product_tier
        ORDER BY country_name, product_tier
    """),
    columns=["country", "product_tier", "in_arrears", "total", "arrears_pct"]
)
pivot_arr = adf.pivot(index="country", columns="product_tier", values="arrears_pct").fillna(0)
tiers     = pivot_arr.columns.tolist()
x         = np.arange(len(pivot_arr.index))
width     = 0.35
tier_colors = {"New": ACCENT, "Refurbished": WARN}

fig, ax = plt.subplots(figsize=(9, 4))
for j, tier in enumerate(tiers):
    offset = (j - len(tiers) / 2 + 0.5) * width
    bars = ax.bar(x + offset, pivot_arr[tier], width,
                  label=tier, color=tier_colors.get(tier, PALETTE[j]),
                  alpha=0.88, edgecolor="#0F1117", linewidth=0.5)
    for bar, val in zip(bars, pivot_arr[tier]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=9)
ax.set_title("Arrears Rate (%) by Country & Product Tier", pad=10)
ax.set_xlabel("Country")
ax.set_ylabel("Arrears Rate (%)")
ax.set_xticks(x)
ax.set_xticklabels(pivot_arr.index)
ax.legend(framealpha=0.15)
ax.set_ylim(0, adf["arrears_pct"].max() * 1.25)
plt.tight_layout()
plt.savefig("reports/04_arrears_by_country_tier.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  ✓ reports/04_arrears_by_country_tier.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 5 — Lead Source Mix by Country
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 5: Lead Source Mix...")

ldf = pd.DataFrame(
    client.execute("""
        SELECT
            country_name,
            lead_source_name,
            count() AS sales_count
        FROM sunculture_db.mart_sales_performance
        GROUP BY country_name, lead_source_name
        ORDER BY country_name, sales_count DESC
    """),
    columns=["country", "lead_source", "count"]
)
country_list = sorted(ldf["country"].unique())
fig, axes = plt.subplots(1, len(country_list), figsize=(14, 5))
if len(country_list) == 1:
    axes = [axes]
fig.suptitle("Lead Source Mix by Country", fontsize=13, fontweight="bold")
for ax, country in zip(axes, country_list):
    subset = ldf[ldf["country"] == country].sort_values("count", ascending=True)
    bars = ax.barh(subset["lead_source"], subset["count"],
                   color=PALETTE[:len(subset)], alpha=0.88,
                   edgecolor="#0F1117", linewidth=0.4)
    for bar in bars:
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f"{int(bar.get_width())}", va="center", fontsize=8)
    ax.set_title(country)
    ax.set_xlabel("Sales Count")
plt.tight_layout()
plt.savefig("reports/05_lead_source_mix.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  ✓ reports/05_lead_source_mix.png")


print("\n" + "="*55)
print("ALL 5 CHARTS GENERATED — see reports/ directory")
print("="*55)
