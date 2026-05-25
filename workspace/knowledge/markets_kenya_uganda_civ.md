# Markets: Kenya, Uganda, Côte d'Ivoire

## Portfolio context

Assessment customers are split roughly across three regions (~1.6k each).

## Kenya — premium loan use case

Marketing briefs often focus on **stable, mid-to-high income proxy** customers:

- High `repayment_progress`, low `is_default`, low `is_in_arrears`
- Prefer **New** product tier and moderate PAYG share
- Channels: field agents, SMS, WhatsApp (assisted sale for credit products)

## Risk patterns (typical EDA themes)

- Arrears varies by **product tier** (Refurbished vs New)
- **PAYG** arrears dynamics differ from CASH
- **Lead source** quality correlates with downstream arrears
- Installation delay anomalies (~negative delays) indicate date alignment issues — treat carefully in ops recommendations
