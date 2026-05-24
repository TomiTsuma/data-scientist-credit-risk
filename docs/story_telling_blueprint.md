# Exploratory Data Analysis & Storytelling Blueprint for SunCulture Senior Data Scientist Assessment

## Objective

* Strong analytical thinking
* Business intuition
* Data storytelling ability
* Cross-functional reasoning
* Executive-level communication
* Ability to identify operational and revenue opportunities
* Ability to identify risk patterns

The notebook should feel like a quarterly business review prepared for country leadership teams in:

* Kenya
* Uganda
* Côte d’Ivoire

Analysis should answer:

> “What important operational, commercial, and risk patterns are emerging that leadership is not already seeing in standard dashboards?”

---

# 1. Understand the Dataset Structure

The dataset appears to represent a customer acquisition-to-installation-to-account lifecycle.

## Main Tables

| Table         | Business Meaning                                |
| ------------- | ----------------------------------------------- |
| Customers     | Customer demographics and geography             |
| Leads         | Lead acquisition sources                        |
| Accounts      | Commercial account status and payment structure |
| Sales         | Final sales events                              |
| Installations | Installation operations                         |
| Products      | Product catalog                                 |
| Users         | Internal employees/agents/engineers             |
| Departments   | Organizational structure                        |

---

# 2. Recommended Notebook Structure

Your notebook should feel like a professional consulting or internal strategy analysis.

Recommended sections:

---

## Section 1 — Executive Summary

A concise summary for leadership.

Example structure:

* Key growth findings
* Operational bottlenecks
* Credit/payment risks
* Regional performance differences
* Recommended business actions

Keep this section short.

Think:

> “If the CEO only reads one page, what should they know?”

---

## Section 2 — Data Understanding & Data Quality

Demonstrate professionalism.

### Include:

* Table shapes
* Relationship mapping
* Missing values
* Duplicate checks
* Data types
* Date parsing
* Join logic
* Cardinality validation

### Mention:

* Accounts is likely the central fact table
* Customers, Leads, Products, Users are dimensions

---

## Section 3 — Data Preparation

Create analytical datasets.

### Suggested derived fields:

---

## Customer Age

From Date_of_birth.

Useful for:

* segmentation
* risk patterns
* regional demographics

Potential grouping:

* <25
* 25–35
* 35–50
* 50+

---

## Installation Delay

Potential metric:

Installation_date - Sale_date

Business meaning:

* operational efficiency
* fulfillment quality
* regional logistics bottlenecks

---

## Lead-to-Sale Conversion

Create flags:

* lead converted
* account created
* installation completed

This enables funnel analysis.

---

## Payment Risk Indicators

From Accounts table:

Account status categories:

* Complete
* Active
* Arrears
* Default
* Pending

You can create:

* risky account flag
* arrears rate
* completion rate

---

## Sales Cohorts

Create:

* monthly cohorts
* quarterly cohorts
* country cohorts

Useful for trend analysis.

---

# 3. Recommended Business Storylines (Very Important)

The strongest notebooks usually tell 4–5 coherent stories.

Do NOT produce random charts.

Each section should answer:

1. What happened?
2. Why does it matter?
3. What action should leadership consider?

---

# STORY 1 — Regional Revenue & Growth Performance

## Business Question

Which countries are driving commercial growth, and are there signs of slowing momentum or operational inefficiencies?

---

## Metrics

### Core KPIs

* Total sales by region
* Monthly sales trend
* Account creation trend
* Installations completed
* Revenue proxy (sales volume)
* Growth rate by quarter

---

## Recommended Visualizations

### Visualization 1 — Monthly Sales Trend by Region

Use:

* line chart

Purpose:

* compare Kenya vs Uganda vs Côte d’Ivoire
* identify acceleration or slowdown

---

### Visualization 2 — Regional Sales Contribution

Use:

* stacked bar chart
  or
* area chart

Purpose:

* show country contribution to overall business

---

## Potential Insights

Examples:

* Uganda may show stronger growth but weaker completion rates
* Kenya may dominate installations but show slowing new customer acquisition
* Côte d’Ivoire may be underpenetrated but growing rapidly

---

## Business Impact

This affects:

* expansion strategy
* resource allocation
* inventory planning
* hiring decisions

---

## Recommended Actions

Examples:

* increase marketing investment in fast-growing regions
* investigate declining lead generation trends
* improve regional operational support

---

# STORY 2 — Lead Source Effectiveness & Conversion Funnel

## Business Question

Which acquisition channels generate the highest quality customers?

This is extremely important because leadership cares about:

* marketing efficiency
* CAC optimization
* scalable growth

---

## Metrics

### Funnel Metrics

For each lead source:

* number of leads
* account creation rate
* installation completion rate
* arrears/default rate
* conversion-to-sale rate

---

## Recommended Visualizations

### Visualization 1 — Funnel Conversion by Lead Source

Use:

* funnel chart
  or
* grouped bar chart

---

### Visualization 2 — Heatmap

Rows:

* lead source

Columns:

* conversion metrics
* arrears rates
* completion rates

Purpose:

* identify high-quality vs low-quality channels

---

## Potential Insights

Examples:

* Roadshows may generate high volume but poor repayment quality
* Referrals may generate fewer leads but stronger account completion
* Digital campaigns may have faster conversion cycles

---

## Business Impact

Directly influences:

* marketing budget allocation
* field activation strategy
* partnership investment

---

## Recommended Actions

Examples:

* shift spend toward higher-quality channels
* redesign low-performing campaigns
* create referral incentives

---

# STORY 3 — Credit Risk & Account Health Analysis

This is likely one of the strongest sections for this role.

The role explicitly mentions:

* credit scoring
* predictive analytics
* collections optimization

This section can strongly differentiate you.

---

## Business Question

What customer or operational patterns are associated with account risk?

---

## Metrics

### Account Health KPIs

* arrears rate by region
* default rate by product
* risk rate by lead source
* risk rate by payment type
* active vs complete accounts
* PAYG vs CASH risk comparison

---

## Recommended Visualizations

### Visualization 1 — Account Status Distribution

Use:

* stacked bar chart

Breakdown:

* by country
* by product
* by payment type

---

### Visualization 2 — Risk Heatmap

Axes:

* region
* product/payment type

Metric:

* arrears/default percentage

---

### Visualization 3 — Cohort Risk Trend

Track:

* arrears/default rates over time

Purpose:

* detect worsening repayment trends

---

## Potential Insights

Examples:

* PAYG customers may exhibit higher arrears rates
* Certain products may correlate with increased payment stress
* Specific regions may show worsening repayment quality
* Some lead channels may attract higher-risk customers

---

## Business Impact

This directly affects:

* portfolio quality
* revenue predictability
* collections costs
* future credit losses

---

## Recommended Actions

Examples:

* tighten credit policies for risky segments
* improve collections prioritization
* introduce targeted customer education
* refine credit scoring models

---

# STORY 4 — Operational Efficiency & Installation Bottlenecks

This is another very strong operational insight area.

---

## Business Question

Are installation operations scaling efficiently across regions?

---

## Metrics

### Operational KPIs

* installation turnaround time
* installations per engineer
* regional installation delays
* backlog rates
* agent-to-installation conversion speed

---

## Recommended Visualizations

### Visualization 1 — Distribution of Installation Delays

Use:

* histogram
  or
* violin plot

Purpose:

* identify long-tail operational delays

---

### Visualization 2 — Regional Delay Comparison

Use:

* boxplot

Purpose:

* compare operational consistency across countries

---

### Visualization 3 — Engineer Productivity

Use:

* ranked bar chart

Metrics:

* installations completed per engineer

---

## Potential Insights

Examples:

* some regions may experience significantly longer installation cycles
* operational bottlenecks may correlate with specific engineers or regions
* scaling sales may be outpacing installation capacity

---

## Business Impact

Operational delays can affect:

* customer satisfaction
* activation speed
* repayment start dates
* cash flow timing

---

## Recommended Actions

Examples:

* optimize engineer allocation
* improve logistics planning
* increase staffing in bottleneck regions
* improve dispatch coordination

---

# STORY 5 — Product Mix & Strategic Expansion Opportunities

## Business Question

Which products are driving adoption, and which may require strategic attention?

---

## Metrics

* product adoption by region
* refurb vs non-refurb performance
* product-linked arrears rates
* growth trends by product
* installation success by product

---

## Recommended Visualizations

### Visualization 1 — Product Adoption by Region

Use:

* stacked bar chart

---

### Visualization 2 — Product Risk Matrix

Use:

* scatter plot

Axes:

* sales volume
* arrears/default rate

Purpose:

* identify:

  * high-growth low-risk products
  * high-growth high-risk products

---

## Potential Insights

Examples:

* refurbished products may drive affordability but increase operational issues
* certain products may perform exceptionally well in specific countries
* product complexity may influence repayment quality

---

## Business Impact

This affects:

* inventory strategy
* pricing
* financing structure
* regional expansion

---

## Recommended Actions

Examples:

* prioritize strong-performing products
* redesign financing for risky products
* localize product strategy by country

---

# 4. Strong Visualization Recommendations

Avoid default charts everywhere.

Choose visuals intentionally.

---

## Best Visualization Types

| Goal                   | Recommended Visualization         |
| ---------------------- | --------------------------------- |
| Trends over time       | Line chart                        |
| Regional comparison    | Grouped/stacked bar chart         |
| Risk intensity         | Heatmap                           |
| Distribution analysis  | Histogram / boxplot / violin plot |
| Funnel analysis        | Funnel chart                      |
| Correlation analysis   | Correlation heatmap               |
| Operational efficiency | Scatter plot                      |
| Segment comparison     | Treemap / stacked bars            |

---

# 5. Advanced Analysis Ideas (Optional but Impressive)

If you want to stand out:

---

## A. Cohort Analysis

Track customer/account behavior by signup month.

Example:

* repayment quality by acquisition cohort

Very strong business insight.

---

## B. Geographic Mapping

Use latitude/longitude.

Potential insights:

* regional clusters
* underserved areas
* operational concentration

Use:

* Folium
* Plotly maps

---

## C. Customer Segmentation

Simple clustering:

* customer age
* payment type
* product type
* region
* risk status

Purpose:

* identify customer personas

---

## D. Survival / Time-to-Event Analysis

Analyze:

* time from lead → sale
* sale → installation

Excellent operational insight.

---

# 6. Suggested Narrative Flow

This is VERY important.

A strong notebook feels like a strategic story.

Recommended flow:

1. Business growth overview
2. Customer acquisition quality
3. Risk & repayment patterns
4. Operational bottlenecks
5. Strategic opportunities
6. Executive recommendations

This creates a coherent leadership narrative.

---

# 7. What Makes the Notebook Look Senior-Level

To look senior:

---

## Explain WHY Metrics Matter

Not just:

> “Uganda has more arrears.”

Instead:

> “Uganda’s increasing arrears rate alongside rapid account growth may indicate that expansion is outpacing credit risk controls.”

---

## Connect Findings Across Functions

Example:

* marketing quality
* operational delays
* repayment risk

Senior analysts connect systems together.

---

## Focus on Decisions

Every insight should answer:

> “What should leadership potentially do?”

---

## Use Executive Language

Use terms like:

* operational efficiency
* portfolio quality
* customer acquisition efficiency
* growth sustainability
* repayment behavior
* activation bottlenecks
* regional performance variance

---

# 8. Final Executive Recommendations Section

End with a concise recommendation section.

Example structure:

---

## Recommendation 1

Reallocate marketing spend toward high-conversion lead sources with lower arrears rates.

---

## Recommendation 2

Investigate operational bottlenecks in regions with prolonged installation delays.

---

## Recommendation 3

Enhance credit monitoring for rapidly growing PAYG segments showing increasing arrears.

---

## Recommendation 4

Develop region-specific product and financing strategies based on repayment performance.

---

# 9. What Interviewers Will Actually Evaluate

They are likely evaluating:

| Area              | What They Want                            |
| ----------------- | ----------------------------------------- |
| SQL/data skills   | Ability to structure relational analysis  |
| Analytics         | Ability to identify patterns              |
| Product thinking  | Understanding operational/business impact |
| Communication     | Ability to explain insights clearly       |
| Leadership        | Strategic recommendations                 |
| Data storytelling | Narrative-driven analysis                 |
| Seniority         | Cross-functional reasoning                |

---