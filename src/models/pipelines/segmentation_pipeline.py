from src.features.segmentation_features import create_segmentation_features


def run_segmentation_pipeline(df):
    return create_segmentation_features(df)
