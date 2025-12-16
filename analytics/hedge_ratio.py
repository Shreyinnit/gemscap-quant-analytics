import pandas as pd
import statsmodels.api as sm


def compute_hedge_ratio(df, symbol_y, symbol_x):
    """
    Compute OLS hedge ratio between two symbols.
    Y = beta * X + epsilon
    """

    # Filter symbols
    y_df = df[df["symbol"] == symbol_y][["timestamp", "price"]]
    x_df = df[df["symbol"] == symbol_x][["timestamp", "price"]]

    # Align timestamps
    merged = pd.merge(
        y_df, x_df, on="timestamp", how="inner", suffixes=("_y", "_x")
    )

    if merged.empty:
        return None, None

    X = sm.add_constant(merged["price_x"])
    y = merged["price_y"]

    model = sm.OLS(y, X).fit()

    hedge_ratio = model.params["price_x"]

    return hedge_ratio, merged
