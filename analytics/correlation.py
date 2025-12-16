import pandas as pd


def compute_rolling_correlation(merged_df, window=30):
    """
    Compute rolling correlation between two price series.
    """

    df = merged_df.copy()

    df["rolling_corr"] = (
        df["price_y"]
        .rolling(window)
        .corr(df["price_x"])
    )

    return df
