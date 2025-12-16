import pandas as pd


def resample_ticks(df, timeframe="1min"):
    """
    Resample tick-level data into OHLC-style bars.

    Parameters:
    df : DataFrame with columns [timestamp, symbol, price, size]
    timeframe : str -> '1s', '1min', '5min'

    Returns:
    Resampled DataFrame
    """

    if df.empty:
        return df

    df = df.copy()
    df.set_index("timestamp", inplace=True)

    resampled = (
        df
        .groupby("symbol")
        .resample(timeframe)
        .agg({
            "price": "last",   # last traded price
            "size": "sum"      # total volume
        })
        .dropna()
        .reset_index()
    )

    return resampled
