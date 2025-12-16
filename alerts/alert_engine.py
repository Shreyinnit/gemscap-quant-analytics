def check_zscore_alert(zscore, threshold):
    if zscore is None:
        return False

    return abs(zscore) > threshold
