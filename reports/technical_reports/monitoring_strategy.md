# Monitoring Strategy

## Segmentation model

| Metric | Source | Alert threshold |
|--------|--------|-----------------|
| Feature PSI | Batch compare vs training snapshot | PSI > 0.2 |
| Segment size share | Daily counts by `segment_id` | > 15% shift in 30d |
| API latency p95 | `/api/segment` | > 500ms |
| Error rate | API 5xx | > 1% over 15m |

## Implementation

- `src/deployment/monitoring/drift_detection.py` — extend `detect_promotion_drift` with PSI per numeric feature.
- `src/deployment/monitoring/metrics.py` — export Prometheus counters for scoring volume.
- `src/deployment/monitoring/alerts.py` — webhook to Slack/PagerDuty on threshold breach.

## Retrain triggers

1. Scheduled quarterly retrain on latest mart.
2. PSI breach on ≥ 3 features.
3. Product/policy change (new tier, new country).
