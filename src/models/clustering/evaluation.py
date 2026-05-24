"""Cluster count selection diagnostics."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import calinski_harabasz_score, silhouette_score


def evaluate_clustering(features: np.ndarray, labels: np.ndarray) -> float:
    if len(np.unique(labels)) < 2:
        return -1.0
    return float(silhouette_score(features, labels))


def cluster_metrics(features: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    n_clusters = len(np.unique(labels))
    if n_clusters < 2:
        return {"silhouette": -1.0, "calinski_harabasz": 0.0}
    return {
        "silhouette": float(silhouette_score(features, labels)),
        "calinski_harabasz": float(calinski_harabasz_score(features, labels)),
    }


def evaluate_k_range(
    features: np.ndarray,
    k_min: int = 2,
    k_max: int = 10,
    random_state: int = 42,
) -> list[dict]:
    """Inertia, silhouette, and cluster size validity for k selection."""
    from src.models.clustering.kmeans import build_kmeans_model

    n = len(features)
    results = []
    for k in range(k_min, k_max + 1):
        model = build_kmeans_model(n_clusters=k, random_state=random_state)
        labels = model.fit_predict(features)
        sizes = np.bincount(labels)
        min_pct = sizes.min() / n * 100
        metrics = cluster_metrics(features, labels)
        results.append(
            {
                "k": k,
                "inertia": float(model.inertia_),
                "silhouette": metrics["silhouette"],
                "calinski_harabasz": metrics["calinski_harabasz"],
                "min_cluster_pct": float(min_pct),
            }
        )
    return results


def select_optimal_k(
    results: list[dict],
    min_cluster_pct: float = 5.0,
    prefer_k_range: tuple[int, int] = (4, 6),
    silhouette_tolerance: float = 0.05,
) -> int:
    """Pick k balancing silhouette and business granularity (4–6 personas)."""
    valid = [r for r in results if r["min_cluster_pct"] >= min_cluster_pct]
    if not valid:
        valid = results
    best_sil = max(r["silhouette"] for r in valid)
    lo, hi = prefer_k_range
    in_range = [
        r
        for r in valid
        if lo <= r["k"] <= hi and r["silhouette"] >= best_sil - silhouette_tolerance
    ]
    if in_range:
        return int(max(in_range, key=lambda r: r["silhouette"])["k"])
    return int(max(valid, key=lambda r: r["silhouette"])["k"])
