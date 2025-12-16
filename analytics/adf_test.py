from statsmodels.tsa.stattools import adfuller


def run_adf_test(spread_series):
    """
    Run Augmented Dickey-Fuller test on spread.
    """

    spread_series = spread_series.dropna()

    if len(spread_series) < 20:
        return None

    result = adfuller(spread_series)

    return {
        "ADF Statistic": result[0],
        "p-value": result[1],
        "Critical Values": result[4]
    }
