from sklearn.metrics import silhouette_score


def evaluate_clustering(features, labels):
    return silhouette_score(features, labels)
