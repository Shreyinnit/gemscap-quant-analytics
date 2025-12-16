import streamlit as st
import plotly.graph_objects as go

from ingestion.data_loader import load_tick_data
from analytics.resampling import resample_ticks
from analytics.price_stats import compute_price_stats
from analytics.hedge_ratio import compute_hedge_ratio
from analytics.spread_zscore import compute_spread_zscore
from analytics.correlation import compute_rolling_correlation
from analytics.adf_test import run_adf_test
from alerts.alert_engine import check_zscore_alert

# -------------------------------------------------
# PAGE CONFIG (IMPORTANT FOR LAPTOP VIEW)
# -------------------------------------------------
st.set_page_config(
    page_title="Gemscap Quant Analytics",
    layout="wide"
)

st.title("📊 Gemscap Quant Analytics Dashboard")
st.caption(
    "An intuitive real-time analytics dashboard designed for non-technical users."
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
df = load_tick_data()

# -------------------------------------------------
# TIMEFRAME SELECTION
# -------------------------------------------------
st.sidebar.header("⚙️ Controls")

timeframe_label = st.sidebar.selectbox(
    "Select Timeframe",
    ["1s", "1min", "5min"]
)

TF_MAP = {"1s": "1S", "1min": "1min", "5min": "5min"}
timeframe = TF_MAP[timeframe_label]

# -------------------------------------------------
# RESAMPLING
# -------------------------------------------------
resampled_df = resample_ticks(df, timeframe)
symbols = resampled_df["symbol"].unique().tolist()

# -------------------------------------------------
# 📈 MARKET SNAPSHOT
# -------------------------------------------------
st.header("📈 Market Snapshot")

col1, col2 = st.columns(2)

# --- Price Chart ---
fig_price = go.Figure()
for symbol in symbols:
    sym_df = resampled_df[resampled_df["symbol"] == symbol]
    fig_price.add_trace(go.Scatter(
        x=sym_df["timestamp"],
        y=sym_df["price"],
        mode="lines",
        name=symbol
    ))

fig_price.update_layout(title="Price Movement Over Time")

with col1:
    st.subheader("Price Movement")
    st.caption("Shows how prices change over time.")
    st.plotly_chart(fig_price, use_container_width=True)

# --- Volume Chart ---
fig_vol = go.Figure()
for symbol in symbols:
    sym_df = resampled_df[resampled_df["symbol"] == symbol]
    fig_vol.add_trace(go.Bar(
        x=sym_df["timestamp"],
        y=sym_df["size"],
        name=symbol
    ))

fig_vol.update_layout(title="Trading Activity (Volume)", barmode="overlay")

with col2:
    st.subheader("Trading Activity")
    st.caption("Higher bars mean more people are trading.")
    st.plotly_chart(fig_vol, use_container_width=True)

# -------------------------------------------------
# 📊 PRICE STATISTICS
# -------------------------------------------------
st.header("📊 Price Behavior")

window = st.sidebar.slider("Rolling Window", 5, 100, 30)
stats_df = compute_price_stats(resampled_df, window)

col1, col2 = st.columns([1.2, 1.8])

with col1:
    st.subheader("Recent Statistics")
    st.caption("Latest calculated price metrics.")
    st.dataframe(
        stats_df[
            ["symbol", "timestamp", "price", "log_return"]
        ].tail(10),
        use_container_width=True
    )

# --- Volatility ---
fig_volatility = go.Figure()
for symbol in symbols:
    sym_df = stats_df[stats_df["symbol"] == symbol]
    fig_volatility.add_trace(go.Scatter(
        x=sym_df["timestamp"],
        y=sym_df["rolling_volatility"],
        mode="lines",
        name=symbol
    ))

fig_volatility.update_layout(title="Price Volatility")

with col2:
    st.subheader("Volatility")
    st.caption("Higher values mean higher risk or instability.")
    st.plotly_chart(fig_volatility, use_container_width=True)

# -------------------------------------------------
# 🔗 ASSET CONNECTION
# -------------------------------------------------
st.header("🔗 How Are These Assets Connected?")

symbol_y = st.sidebar.selectbox("Primary Asset (Y)", symbols)
symbol_x = st.sidebar.selectbox("Secondary Asset (X)", symbols, index=1)

hedge_ratio, merged_df = compute_hedge_ratio(stats_df, symbol_y, symbol_x)

corr_window = st.sidebar.slider("Correlation Window", 10, 100, 30)
corr_df = compute_rolling_correlation(merged_df, corr_window)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Relationship Strength")
    st.metric("Hedge Ratio", f"{hedge_ratio:.2f}")
    st.caption(
        "Shows how much one asset typically moves when the other moves."
    )

fig_corr = go.Figure()
fig_corr.add_trace(go.Scatter(
    x=corr_df["timestamp"],
    y=corr_df["rolling_corr"],
    mode="lines"
))
fig_corr.update_layout(title="Do Prices Move Together?")

with col2:
    st.subheader("Price Relationship")
    st.caption("Values near +1 mean strong connection.")
    st.plotly_chart(fig_corr, use_container_width=True)

# -------------------------------------------------
# 📊 IS TODAY NORMAL OR UNUSUAL?
# -------------------------------------------------
st.header("📊 Is Today Normal or Unusual?")

z_window = st.sidebar.slider("Z-Score Window", 10, 100, 30)
spread_df = compute_spread_zscore(merged_df, hedge_ratio, z_window)

threshold = st.sidebar.slider("Alert Threshold", 1.0, 4.0, 2.0, 0.1)

col1, col2 = st.columns(2)

# --- Spread ---
fig_spread = go.Figure()
fig_spread.add_trace(go.Scatter(
    x=spread_df["timestamp"],
    y=spread_df["spread"],
    mode="lines"
))
fig_spread.update_layout(title="Price Difference")

with col1:
    st.subheader("Price Difference")
    st.caption("How far prices are from their usual relationship.")
    st.plotly_chart(fig_spread, use_container_width=True)

# --- Z-Score ---
fig_z = go.Figure()
fig_z.add_trace(go.Scatter(
    x=spread_df["timestamp"],
    y=spread_df["zscore"],
    mode="lines"
))
fig_z.add_hline(y=threshold, line_dash="dash", line_color="red")
fig_z.add_hline(y=-threshold, line_dash="dash", line_color="red")
fig_z.add_hline(y=0, line_color="gray")

fig_z.update_layout(title="How Unusual Is It?")

with col2:
    st.subheader("Unusualness Indicator")
    st.caption("Above +2 or below -2 means unusual.")
    st.plotly_chart(fig_z, use_container_width=True)

# -------------------------------------------------
# 🚦 DECISION SUPPORT
# -------------------------------------------------
st.header("🚦 What Should a Trader Do?")

latest_z = spread_df["zscore"].dropna().iloc[-1]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Alert Status")
    if check_zscore_alert(latest_z, threshold):
        st.error(f"🚨 Unusual situation detected (Z = {latest_z:.2f})")
    else:
        st.success("🟢 Market looks normal")

signal = "HOLD"
if latest_z > threshold:
    signal = "SHORT Spread"
elif latest_z < -threshold:
    signal = "LONG Spread"

with col2:
    st.subheader("Suggested Action")
    st.caption("Assumes prices may return to normal.")
    st.info(f"📈 Signal: **{signal}**")

# -------------------------------------------------
# 🧪 STATISTICAL CHECK
# -------------------------------------------------
st.header("🧪 Stability Check")

st.caption("Checks whether price difference usually returns to normal.")

if st.button("Run Stability Test"):
    st.write(run_adf_test(spread_df["spread"]))

# -------------------------------------------------
# 📦 EXPORT
# -------------------------------------------------
st.header("📦 Download Data")

st.download_button(
    "Download Analytics CSV",
    spread_df.to_csv(index=False),
    file_name="pair_analytics.csv"
)
