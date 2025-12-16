import pandas as pd


def compute_spread_zscore(merged_df, hedge_ratio, window=30):
    """
    Compute spread and z-score for a pair.

    spread = Y - beta * X
    z-score = (spread - mean) / std
    """

    df = merged_df.copy()

    # Spread
    df["spread"] = df["price_y"] - hedge_ratio * df["price_x"]

    # Rolling statistics
    df["spread_mean"] = df["spread"].rolling(window).mean()
    df["spread_std"] = df["spread"].rolling(window).std()

    # Z-score
    df["zscore"] = (df["spread"] - df["spread_mean"]) / df["spread_std"]

    return df
