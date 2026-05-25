# Segmentation Methodology (Part 2.1)

- **Algorithm:** K-Means on scaled numeric + one-hot categorical features.
- **k selection:** Best silhouette among k ∈ [4, 6] with each cluster ≥ 5% of customers.
- **Features:** Age, tenure, financed proxy, repayment progress, arrears signals, lead quality, RFM-style scores — see `reports/business_reports/segmentation_report.md`.
- **Limitation:** Unsupervised clusters optimize separation, not campaign ROI; no income field.

Artifacts: `models/segmentation/kmeans_pipeline.joblib`, `data/processed/customer_segments.parquet`.
