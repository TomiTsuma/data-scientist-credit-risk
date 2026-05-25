---
name: customer-segmentation
description: K-Means customer segments, optimal k, and business personas for SunCulture Part 2.
---

# Customer Segmentation

1. `list_customer_segments` for sizes, arrears %, default %, repayment progress.
2. `predict_customer_segment` for a single `customer_id`.
3. `read_business_report` → `segmentation_report` for written profiles.
4. Explain that k was chosen with silhouette + minimum cluster size (see report).
5. For premium loan targeting, exclude segments with high `arrears_rate` unless user asks for contrast.

Income is **not** in the dataset — use financed proxy and product tier only.
