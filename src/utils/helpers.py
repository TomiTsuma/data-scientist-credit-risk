def safe_divide(a, b, default=0.0):
    return a / b if b else default
