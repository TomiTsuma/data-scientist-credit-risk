import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException

from src.config.config import Config
from src.deployment.api.schemas import HealthResponse, SegmentRequest, SegmentResponse
from src.features.segmentation_features import create_segmentation_features
from src.models.clustering.profiling import assign_segment_names
from src.models.clustering.profiling import segment_lifts

router = APIRouter()
CONFIG = Config()
_PIPELINE = None
_SEGMENT_NAMES: dict[int, str] | None = None


def _load_pipeline():
    global _PIPELINE, _SEGMENT_NAMES
    if _PIPELINE is None:
        path = CONFIG.models_dir / "segmentation" / "kmeans_pipeline.joblib"
        if not path.exists():
            raise FileNotFoundError(
                "Segmentation model not found. Run: python3.11 scripts/run_part2_pipeline.py"
            )
        _PIPELINE = joblib.load(path)
        card_path = CONFIG.models_dir / "segmentation" / "model_card.json"
        if card_path.exists():
            import json

            card = json.loads(card_path.read_text(encoding="utf-8"))
            _SEGMENT_NAMES = {int(k): v for k, v in card.get("segment_names", {}).items()}
    return _PIPELINE


@router.get("/health", response_model=HealthResponse)
def health_check():
    model_path = CONFIG.models_dir / "segmentation" / "kmeans_pipeline.joblib"
    return {
        "status": "healthy" if model_path.exists() else "degraded",
        "version": "0.2.0",
    }


@router.post("/segment", response_model=SegmentResponse)
def predict_segment(payload: SegmentRequest):
    try:
        pipeline = _load_pipeline()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    row = payload.model_dump()
    df = pd.DataFrame([row])
    featured = create_segmentation_features(df)
    segment_id = int(pipeline.predict(featured)[0])

    name = "Unknown"
    if _SEGMENT_NAMES and segment_id in _SEGMENT_NAMES:
        name = _SEGMENT_NAMES[segment_id]
    else:
        lifts = segment_lifts(featured.assign(segment_id=segment_id), "segment_id")
        names = assign_segment_names(lifts)
        name = names.get(segment_id, f"Segment {segment_id}")

    return SegmentResponse(
        segment_id=segment_id,
        segment_name=name,
        customer_id=payload.customer_id,
    )
