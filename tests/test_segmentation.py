import pandas as pd
import pytest

from src.models.clustering.evaluation import evaluate_k_range, select_optimal_k
from src.models.pipelines.segmentation_pipeline import fit_segmentation


@pytest.fixture(scope="module")
def segmentation_result():
    try:
        return fit_segmentation(k_max=6)
    except FileNotFoundError:
        pytest.skip("Assessment data not available")


def test_optimal_k_in_range():
    import numpy as np

    rng = np.random.default_rng(42)
    x = rng.normal(size=(200, 5))
    results = evaluate_k_range(x, k_min=2, k_max=6)
    k = select_optimal_k(results)
    assert 2 <= k <= 6


def test_segmentation_produces_segments(segmentation_result):
    df = segmentation_result.customer_df
    assert segmentation_result.optimal_k >= 2
    assert "segment_id" in df.columns
    assert df["segment_id"].nunique() == segmentation_result.optimal_k
