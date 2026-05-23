from sklearn.cluster import DBSCAN


def build_dbscan_model(eps: float = 0.5, min_samples: int = 5):
    return DBSCAN(eps=eps, min_samples=min_samples)
