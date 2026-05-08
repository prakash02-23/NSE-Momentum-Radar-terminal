import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from zoneinfo import ZoneInfo

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="NSE Momentum Radar",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# AUTO REFRESH
# =====================================================

st_autorefresh(interval=60000, key="refresh_counter")

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
    color: white;
}

.main-title {
    font-size: 40px;
    font-weight: bold;
    color: white;
}

.block-container {
    padding-top: 1rem;
}

[data-testid="stSidebar"] {
    background-color: #1B1E27;
}

.stock-card {
    padding: 8px;
    border-radius: 10px;
    background-color: #252A36;
    margin-bottom: 6px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# STOCKS
# =====================================================

NIFTY_STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "LT": "LT.NS",
    "AXISBANK": "AXISBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "ITC": "ITC.NS",
    "BEL": "BEL.NS",
    "HAL": "HAL.NS",
    "TRENT": "TRENT.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "SUNPHARMA": "SUNPHARMA.NS"
}

SECTOR_MAP = {
    "RELIANCE": "Energy",
    "TCS": "IT",
    "INFY": "IT",
    "HDFCBANK": "Banking",
    "ICICIBANK": "Banking",
    "SBIN": "Banking",
    "LT": "Infrastructure",
    "AXISBANK": "Banking",
    "KOTAKBANK": "Banking",
    "ITC": "FMCG",
    "BEL": "Defence",
    "HAL": "Defence",
    "TRENT": "Retail",
    "TATAMOTORS": "Auto",
    "SUNPHARMA": "Pharma"
}

# =====================================================
# SESSION STATE
# =====================================================

if "watchlist" not in st.session_state:
    st.session_state.watchlist = [
        "RELIANCE",
        "TCS",
        "INFY",
        "BEL"
    ]

if "selected_chart_stock" not in st.session_state:
    st.session_state.selected_chart_stock = "RELIANCE"

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("📊 Watchlist")

selected_stock = st.sidebar.selectbox(
    "Add Stock",
    sorted(list(NIFTY_STOCKS.keys()))
)

if st.sidebar.button("➕ Add Stock"):
    if selected_stock not in st.session_state.watchlist:
        st.session_state.watchlist.append(selected_stock)

st.sidebar.markdown("---")

st.sidebar.subheader("Current Watchlist")

stocks_to_remove = []

for stock in st.session_state.watchlist:

    col1, col2 = st.sidebar.columns([4, 1])

    with col1:
        st.write(f"• {stock}")

    with col2:
        if st.button("❌", key=f"remove_{stock}"):
            stocks_to_remove.append(stock)

for stock in stocks_to_remove:
    st.session_state.watchlist.remove(stock)

# =====================================================
# HEADER
# =====================================================

ist_time = datetime.now(ZoneInfo("Asia/Kolkata"))

col1, col2, col3 = st.columns([4, 2, 2])

with col1:
    st.markdown(
        '<div class="main-title">🚀 NSE Momentum Radar</div>',
        unsafe_allow_html=True
    )

with col2:

    market_status = "NSE OPEN"

    if (
        ist_time.hour < 9 or
        ist_time.hour > 15 or
        (ist_time.hour == 15 and ist_time.minute > 30)
    ):
        market_status = "NSE CLOSED"

    st.metric("Market", market_status)

with col3:
    st.metric(
        "Indian Time",
        ist_time.strftime("%H:%M:%S")
    )

st.markdown("---")

# =====================================================
# DATA FETCHING
# =====================================================

@st.cache_data(ttl=300)
def fetch_stock_data(symbol):

    try:

        df = yf.download(
            symbol,
            period="5d",
            interval="5m",
            progress=False,
            auto_adjust=True,
            threads=False
        )

        if df is None or df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if len(df) < 20:
            return None

        return df

    except Exception:
        return None

# =====================================================
# MOMENTUM ENGINE
# =====================================================

def calculate_metrics(df):

    try:

        latest_close = float(df["Close"].values[-1])
        prev_close = float(df["Close"].values[-2])

        latest_open = float(df["Open"].values[-1])

        price_change = (
            (latest_close - prev_close) / prev_close
        ) * 100

        volume_avg = df["Volume"].rolling(20).mean().values[-1]

        current_volume = float(df["Volume"].values[-1])

        if volume_avg == 0 or np.isnan(volume_avg):
            relative_volume = 1
        else:
            relative_volume = current_volume / volume_avg

        ema20 = float(
            df["Close"].ewm(span=20).mean().values[-1]
        )

        breakout_high = float(
            df["High"].rolling(20).max().values[-2]
        )

        breakout_distance = (
            latest_close / breakout_high
        ) * 100

        typical_price = (
            df["High"] +
            df["Low"] +
            df["Close"]
        ) / 3

        vwap = float(
            (
                (typical_price * df["Volume"]).cumsum() /
                df["Volume"].cumsum()
            ).values[-1]
        )

        score = 0

        if price_change > 0:
            score += min(price_change * 10, 30)

        score += min(relative_volume * 15, 25)

        if breakout_distance > 98:
            score += 20

        if latest_close > ema20:
            score += 15

        if latest_close > vwap:
            score += 10

        candle_strength = (
            (latest_close - latest_open) / latest_open
        ) * 100

        if candle_strength > 0.5:
            score += 10

        state = "WATCH"

        if score >= 80:
            state = "EXPLOSIVE"
        elif score >= 60:
            state = "BUILDING"
        elif score >= 40:
            state = "ACTIVE"
        elif score >= 20:
            state = "EARLY"

        return {
            "price": round(latest_close, 2),
            "change": round(price_change, 2),
            "rvol": round(relative_volume, 2),
            "score": round(score, 2),
            "state": state,
            "breakout": round(breakout_distance, 2)
        }

    except Exception:
        return None

# =====================================================
# PROCESS WATCHLIST
# =====================================================

momentum_data = []
stock_data_map = {}

for stock in st.session_state.watchlist:

    symbol = NIFTY_STOCKS[stock]

    df = fetch_stock_data(symbol)

    if df is not None:

        metrics = calculate_metrics(df)

        if metrics is not None:

            metrics["stock"] = stock
            metrics["sector"] = SECTOR_MAP.get(stock, "Other")

            momentum_data.append(metrics)
            stock_data_map[stock] = df

# =====================================================
# EMPTY CHECK
# =====================================================

if len(momentum_data) == 0:

    st.warning(
        "No stock data available currently. "
        "Yahoo Finance may be rate limiting requests."
    )

    st.stop()

momentum_df = pd.DataFrame(momentum_data)

# =====================================================
# SORTING
# =====================================================

momentum_df = momentum_df.sort_values(
    by="score",
    ascending=False
).reset_index(drop=True)

momentum_df.index = momentum_df.index + 1
momentum_df.rename_axis("Rank", inplace=True)

# =====================================================
# SELECT STOCK FOR CHART
# =====================================================

selected_chart_stock = st.selectbox(
    "📈 Select Stock For Chart",
    momentum_df["stock"].tolist()
)

st.session_state.selected_chart_stock = selected_chart_stock

# =====================================================
# MOMENTUM LADDER
# =====================================================

st.subheader("⚡ Live Momentum Ladder")

formatted_df = momentum_df.copy()

formatted_df["price"] = formatted_df["price"].map("₹{:,.2f}".format)
formatted_df["change"] = formatted_df["change"].map("{:+.2f}%".format)
formatted_df["rvol"] = formatted_df["rvol"].map("{:.2f}x".format)
formatted_df["score"] = formatted_df["score"].map("{:.2f}".format)
formatted_df["breakout"] = formatted_df["breakout"].map("{:.2f}%".format)

st.dataframe(
    formatted_df,
    use_container_width=True,
    hide_index=False
)

# =====================================================
# HEATMAP
# =====================================================

st.subheader("📈 Sector Momentum Heatmap")

sector_strength = momentum_df.groupby(
    "sector"
)["score"].mean().reset_index()

heatmap_fig = px.treemap(
    sector_strength,
    path=["sector"],
    values="score",
    color="score",
    color_continuous_scale="RdYlGn"
)

heatmap_fig.update_traces(
    textfont_size=28,
    textfont_color="white"
)

heatmap_fig.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font_color="white",
    height=500,
    margin=dict(t=20, l=10, r=10, b=10)
)

st.plotly_chart(
    heatmap_fig,
    use_container_width=True
)

# =====================================================
# CHART
# =====================================================

if selected_chart_stock in stock_data_map:

    chart_stock_data = stock_data_map[selected_chart_stock]

    st.subheader(
        f"📊 Selected Stock Chart — {selected_chart_stock}"
    )

    chart_fig = go.Figure(
        data=[
            go.Candlestick(
                x=chart_stock_data.index,
                open=chart_stock_data["Open"],
                high=chart_stock_data["High"],
                low=chart_stock_data["Low"],
                close=chart_stock_data["Close"]
            )
        ]
    )

    chart_fig.update_layout(
        height=600,
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font_color="white",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
        chart_fig,
        use_container_width=True
    )

# =====================================================
# INSIGHTS
# =====================================================

st.subheader("🧠 Momentum Insights")

selected_row = momentum_df[
    momentum_df["stock"] == selected_chart_stock
].iloc[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Momentum Score ❓",
        selected_row["score"],
        help="Overall momentum strength based on price, volume, breakout and trend"
    )

with col2:
    st.metric(
        "Relative Volume ❓",
        f"{selected_row['rvol']}x",
        help="Shows how much trading volume increased compared to average"
    )

with col3:
    st.metric(
        "Momentum State ❓",
        selected_row["state"],
        help="Current momentum phase of the stock"
    )

with col4:
    st.metric(
        "Breakout Strength ❓",
        f"{selected_row['breakout']}%",
        help="Shows how close stock is to breakout zone"
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "NSE Momentum Radar • Swing Trading Dashboard"
)
