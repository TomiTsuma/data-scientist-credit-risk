"""End-to-end customer segmentation pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from src.config.config import Config
from src.data.joins import build_customer_analytics_table, save_customer_base
from src.features.segmentation_features import (
    build_preprocessor,
    create_segmentation_features,
)
from src.models.clustering.evaluation import evaluate_k_range, select_optimal_k
from src.models.clustering.kmeans import build_kmeans_model
from src.models.clustering.profiling import (
    assign_segment_names,
    profile_cluster_segments,
    segment_lifts,
)

CONFIG = Config()
RANDOM_STATE = 42


@dataclass
class SegmentationResult:
    customer_df: pd.DataFrame
    optimal_k: int
    k_evaluation: list[dict]
    profile: pd.DataFrame
    lifts: pd.DataFrame
    segment_names: dict[int, str]
    pipeline: Pipeline
    model_dir: Path


def fit_segmentation(
    df: pd.DataFrame | None = None,
    k: int | None = None,
    k_max: int = 8,
) -> SegmentationResult:
    if df is None:
        df = build_customer_analytics_table()

    featured = create_segmentation_features(df)
    save_customer_base(featured)

    preprocessor = build_preprocessor()
    X = preprocessor.fit_transform(featured)

    k_eval = evaluate_k_range(X, k_min=2, k_max=k_max, random_state=RANDOM_STATE)
    optimal_k = k if k is not None else select_optimal_k(k_eval)

    kmeans = build_kmeans_model(n_clusters=optimal_k, random_state=RANDOM_STATE)
    labels = kmeans.fit_predict(X)

    featured = featured.copy()
    featured["segment_id"] = labels

    full_pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("cluster", kmeans),
        ]
    )
    # Refit as unified pipeline
    full_pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("cluster", build_kmeans_model(n_clusters=optimal_k, random_state=RANDOM_STATE)),
        ]
    )
    full_pipeline.fit(featured)

    profile = profile_cluster_segments(featured, "segment_id")
    lifts = segment_lifts(featured, "segment_id")
    names = assign_segment_names(lifts)

    featured["segment_name"] = featured["segment_id"].map(names)

    model_dir = CONFIG.models_dir / "segmentation"
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(full_pipeline, model_dir / "kmeans_pipeline.joblib")
    (model_dir / "model_card.json").write_text(
        json.dumps(
            {
                "model_type": "KMeans",
                "n_clusters": optimal_k,
                "random_state": RANDOM_STATE,
                "k_evaluation": k_eval,
                "segment_names": {str(k): v for k, v in names.items()},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    processed = CONFIG.processed_dir
    processed.mkdir(parents=True, exist_ok=True)
    featured[["customer_id", "segment_id", "segment_name", "country_name"]].to_parquet(
        processed / "customer_segments.parquet",
        index=False,
    )

    return SegmentationResult(
        customer_df=featured,
        optimal_k=optimal_k,
        k_evaluation=k_eval,
        profile=profile,
        lifts=lifts,
        segment_names=names,
        pipeline=full_pipeline,
        model_dir=model_dir,
    )


def score_customers(df: pd.DataFrame, pipeline: Pipeline | None = None) -> np.ndarray:
    if pipeline is None:
        pipeline = joblib.load(CONFIG.models_dir / "segmentation" / "kmeans_pipeline.joblib")
    featured = create_segmentation_features(df)
    return pipeline.predict(featured)
