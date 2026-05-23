from sklearn.metrics import roc_auc_score, accuracy_score


def evaluate_risk_model(y_true, y_pred):
    return {
        'roc_auc': roc_auc_score(y_true, y_pred),
        'accuracy': accuracy_score(y_true, (y_pred >= 0.5).astype(int)),
    }
