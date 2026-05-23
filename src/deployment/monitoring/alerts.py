def build_alert_message(metric_name: str, value: float) -> str:
    return f'Alert: {metric_name} reached {value:.2f}'
