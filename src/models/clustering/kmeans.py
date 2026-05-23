from sklearn.cluster import KMeans


def build_kmeans_model(n_clusters: int = 4):
    return KMeans(n_clusters=n_clusters, random_state=42)
