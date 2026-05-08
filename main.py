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

st_autorefresh(interval=10000, key="refresh_counter")

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
    font-size: 34px;
    font-weight: bold;
    color: white;
}

.metric-container {
    background-color: #1C1F26;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #2E323B;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# STOCK LIST
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
    "BAJFINANCE": "BAJFINANCE.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "MARUTI": "MARUTI.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "TITAN": "TITAN.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "NTPC": "NTPC.NS",
    "POWERGRID": "POWERGRID.NS",
    "HCLTECH": "HCLTECH.NS",
    "BEL": "BEL.NS",
    "HAL": "HAL.NS",
    "TRENT": "TRENT.NS",
    "DLF": "DLF.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "INDIGO": "INDIGO.NS",
    "DIVISLAB": "DIVISLAB.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS"
}

# =====================================================
# SECTOR MAP
# =====================================================

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
    "BAJFINANCE": "Finance",
    "ASIANPAINT": "Paint",
    "MARUTI": "Auto",
    "BHARTIARTL": "Telecom",
    "TITAN": "Retail",
    "SUNPHARMA": "Pharma",
    "ULTRACEMCO": "Cement",
    "NTPC": "Power",
    "POWERGRID": "Power",
    "HCLTECH": "IT",
    "BEL": "Defence",
    "HAL": "Defence",
    "TRENT": "Retail",
    "DLF": "Realty",
    "ADANIPORTS": "Logistics",
    "TATAMOTORS": "Auto",
    "JSWSTEEL": "Metal",
    "INDIGO": "Aviation",
    "DIVISLAB": "Pharma",
    "BAJAJFINSV": "Finance"
}

# =====================================================
# SESSION STATE
# =====================================================

if "watchlist" not in st.session_state:
    st.session_state.watchlist = [
        "RELIANCE",
        "TCS",
        "INFY",
        "HDFCBANK",
        "BEL"
    ]

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("📊 Watchlist Manager")

selected_stock = st.sidebar.selectbox(
    "Search Stock",
    sorted(list(NIFTY_STOCKS.keys()))
)

if st.sidebar.button("➕ Add Stock"):
    if selected_stock not in st.session_state.watchlist:
        st.session_state.watchlist.append(selected_stock)

if len(st.session_state.watchlist) > 0:

    remove_stock = st.sidebar.selectbox(
        "Remove Stock",
        st.session_state.watchlist
    )

    if st.sidebar.button("❌ Remove Stock"):
        st.session_state.watchlist.remove(remove_stock)

st.sidebar.markdown("---")

st.sidebar.subheader("Current Watchlist")

for stock in st.session_state.watchlist:
    st.sidebar.write(f"• {stock}")

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
        (ist_time.hour == 15 and ist_time.minute > 30) or
        ist_time.hour > 15
    ):
        market_status = "NSE CLOSED"

    st.metric("Market Status", market_status)

with col3:
    st.metric(
        "Indian Time",
        ist_time.strftime("%H:%M:%S")
    )

st.markdown("---")

# =====================================================
# DATA FETCHING
# =====================================================

@st.cache_data(ttl=30)
def fetch_stock_data(symbol):

    try:
        df = yf.download(
            symbol,
            period="5d",
            interval="5m",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

        return df

    except Exception:
        return None

# =====================================================
# MOMENTUM CALCULATION
# =====================================================

def calculate_metrics(df):

    latest_close = float(df["Close"].iloc[-1])
    prev_close = float(df["Close"].iloc[-2])

    price_change = (
        (latest_close - prev_close) / prev_close
    ) * 100

    volume_avg = df["Volume"].rolling(20).mean().iloc[-1]
    current_volume = df["Volume"].iloc[-1]

    if volume_avg == 0:
        relative_volume = 1
    else:
        relative_volume = current_volume / volume_avg

    ema20 = df["Close"].ewm(span=20).mean().iloc[-1]

    breakout_high = df["High"].rolling(20).max().iloc[-2]

    breakout_distance = (
        latest_close / breakout_high
    ) * 100

    # VWAP
    typical_price = (
        df["High"] +
        df["Low"] +
        df["Close"]
    ) / 3

    vwap = (
        (typical_price * df["Volume"]).cumsum() /
        df["Volume"].cumsum()
    ).iloc[-1]

    # MOMENTUM SCORE
    score = 0

    # Price Momentum
    if price_change > 0:
        score += min(price_change * 10, 30)

    # Relative Volume
    score += min(relative_volume * 15, 25)

    # Breakout
    if breakout_distance > 98:
        score += 20

    # EMA
    if latest_close > ema20:
        score += 15

    # VWAP
    if latest_close > vwap:
        score += 10

    # Candle Strength
    candle_strength = (
        (df["Close"].iloc[-1] - df["Open"].iloc[-1]) /
        df["Open"].iloc[-1]
    ) * 100

    if candle_strength > 0.5:
        score += 10

    # Momentum State
    momentum_state = "WATCH"

    if score >= 80:
        momentum_state = "EXPLOSIVE"
    elif score >= 60:
        momentum_state = "BUILDING"
    elif score >= 40:
        momentum_state = "ACTIVE"
    elif score >= 20:
        momentum_state = "EARLY"

    return {
        "price": round(latest_close, 2),
        "change": round(price_change, 2),
        "rvol": round(relative_volume, 2),
        "ema20": round(ema20, 2),
        "vwap": round(vwap, 2),
        "score": round(score, 2),
        "state": momentum_state,
        "breakout": round(breakout_distance, 2)
    }

# =====================================================
# PROCESS WATCHLIST
# =====================================================

momentum_data = []

chart_stock_data = None
chart_symbol = None

for stock in st.session_state.watchlist:

    symbol = NIFTY_STOCKS[stock]

    df = fetch_stock_data(symbol)

    if df is not None:

        metrics = calculate_metrics(df)

        metrics["stock"] = stock
        metrics["sector"] = SECTOR_MAP.get(stock, "Other")

        momentum_data.append(metrics)

        if chart_stock_data is None:
            chart_stock_data = df
            chart_symbol = stock

# =====================================================
# DISPLAY MOMENTUM TABLE
# =====================================================

if len(momentum_data) > 0:

    momentum_df = pd.DataFrame(momentum_data)

    momentum_df = momentum_df.sort_values(
        by="score",
        ascending=False
    ).reset_index(drop=True)

    momentum_df.index = momentum_df.index + 1

    momentum_df.rename_axis("Rank", inplace=True)

    st.subheader("⚡ Live Momentum Ladder")

    def score_style(val):

        if val >= 80:
            return "background-color: #00AA66; color: white"

        elif val >= 60:
            return "background-color: #2ECC71; color: white"

        elif val >= 40:
            return "background-color: #F1C40F; color: black"

        else:
            return "background-color: #E74C3C; color: white"

    styled_df = momentum_df.style.map(
        score_style,
        subset=["score"]
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400
    )

    # =================================================
    # SECTOR HEATMAP
    # =================================================

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

    heatmap_fig.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font_color="white",
        height=500
    )

    st.plotly_chart(
        heatmap_fig,
        use_container_width=True
    )

    # =================================================
    # CHART SECTION
    # =================================================

    if chart_stock_data is not None:

        st.subheader(f"📊 Selected Stock Chart — {chart_symbol}")

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

    # =================================================
    # AI STYLE INSIGHTS
    # =================================================

    st.subheader("🧠 Momentum Insights")

    top_stock = momentum_df.iloc[0]

    insight_text = f"""
    {top_stock['stock']} is currently leading the momentum ranking.

    Key Signals:
    • Momentum Score: {top_stock['score']}
    • Relative Volume: {top_stock['rvol']}x
    • Momentum State: {top_stock['state']}
    • Sector: {top_stock['sector']}
    • Breakout Strength: {top_stock['breakout']}%
    """

    st.info(insight_text)

else:

    st.warning("No stock data available.")

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "NSE Momentum Radar • Swing Trading Analytics Dashboard"
)
