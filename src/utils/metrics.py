def accuracy_score(y_true, y_pred):
    return sum(y_t == y_p for y_t, y_p in zip(y_true, y_pred)) / len(y_true)
