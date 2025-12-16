import numpy as np
import pandas as pd


def compute_price_stats(df, window=30):
    """
    Compute basic price statistics for resampled data.
    """

    if df.empty:
        return df

    df = df.copy()
    df.sort_values(["symbol", "timestamp"], inplace=True)

    # Log returns (index-safe)
    df["log_return"] = (
        df.groupby("symbol")["price"]
        .transform(lambda x: np.log(x / x.shift(1)))
    )

    # Rolling mean
    df["rolling_mean"] = (
        df.groupby("symbol")["price"]
        .transform(lambda x: x.rolling(window).mean())
    )

    # Rolling standard deviation
    df["rolling_std"] = (
        df.groupby("symbol")["price"]
        .transform(lambda x: x.rolling(window).std())
    )

    # Rolling volatility (std of log returns)
    df["rolling_volatility"] = (
        df.groupby("symbol")["log_return"]
        .transform(lambda x: x.rolling(window).std())
    )

    return df
