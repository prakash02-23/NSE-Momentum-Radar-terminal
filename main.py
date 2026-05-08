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
    background-color: #0B1020;
    color: white;
}

.main-title {
    font-size: 46px;
    font-weight: 900;
    color: white;
}

.section-title {
    font-size: 34px;
    font-weight: 900;
    color: white;
    margin-top: 20px;
    margin-bottom: 10px;
}

.block-container {
    padding-top: 1rem;
}

[data-testid="stSidebar"] {
    background-color: #161B2E;
}

div[data-testid="stMetric"] {
    background-color: #151B2D;
    border: 1px solid #2B3552;
    padding: 12px;
    border-radius: 12px;
}

thead tr th {
    font-size: 18px !important;
    font-weight: bold !important;
    text-transform: uppercase !important;
}

tbody tr td {
    font-size: 16px !important;
    font-weight: 600 !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# COMPLETE NIFTY 50 + NEXT 50
# =====================================================

NIFTY_STOCKS = {

    # NIFTY 50
    "ADANIENT": "ADANIENT.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "APOLLOHOSP": "APOLLOHOSP.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "AXISBANK": "AXISBANK.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "BEL": "BEL.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "BPCL": "BPCL.NS",
    "BRITANNIA": "BRITANNIA.NS",
    "CIPLA": "CIPLA.NS",
    "COALINDIA": "COALINDIA.NS",
    "DRREDDY": "DRREDDY.NS",
    "EICHERMOT": "EICHERMOT.NS",
    "GRASIM": "GRASIM.NS",
    "HCLTECH": "HCLTECH.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "HDFCLIFE": "HDFCLIFE.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS",
    "HINDALCO": "HINDALCO.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "INDUSINDBK": "INDUSINDBK.NS",
    "INFY": "INFY.NS",
    "ITC": "ITC.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "LT": "LT.NS",
    "M&M": "M&M.NS",
    "MARUTI": "MARUTI.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "NTPC": "NTPC.NS",
    "ONGC": "ONGC.NS",
    "POWERGRID": "POWERGRID.NS",
    "RELIANCE": "RELIANCE.NS",
    "SBILIFE": "SBILIFE.NS",
    "SBIN": "SBIN.NS",
    "SHRIRAMFIN": "SHRIRAMFIN.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "TATACONSUM": "TATACONSUM.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "TATASTEEL": "TATASTEEL.NS",
    "TCS": "TCS.NS",
    "TECHM": "TECHM.NS",
    "TITAN": "TITAN.NS",
    "TRENT": "TRENT.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "WIPRO": "WIPRO.NS",

    # NEXT 50
    "ABB": "ABB.NS",
    "ACC": "ACC.NS",
    "AMBUJACEM": "AMBUJACEM.NS",
    "BAJAJHLDNG": "BAJAJHLDNG.NS",
    "BANKBARODA": "BANKBARODA.NS",
    "BERGEPAINT": "BERGEPAINT.NS",
    "BOSCHLTD": "BOSCHLTD.NS",
    "CANBK": "CANBK.NS",
    "CHOLAFIN": "CHOLAFIN.NS",
    "DABUR": "DABUR.NS",
    "DIVISLAB": "DIVISLAB.NS",
    "DLF": "DLF.NS",
    "GAIL": "GAIL.NS",
    "GODREJCP": "GODREJCP.NS",
    "HAL": "HAL.NS",
    "HAVELLS": "HAVELLS.NS",
    "ICICIGI": "ICICIGI.NS",
    "INDIGO": "INDIGO.NS",
    "IOC": "IOC.NS",
    "IRCTC": "IRCTC.NS",
    "JINDALSTEL": "JINDALSTEL.NS",
    "LICI": "LICI.NS",
    "LODHA": "LODHA.NS",
    "MCDOWELL-N": "MCDOWELL-N.NS",
    "MOTHERSON": "MOTHERSON.NS",
    "NAUKRI": "NAUKRI.NS",
    "PIDILITIND": "PIDILITIND.NS",
    "PNB": "PNB.NS",
    "RECLTD": "RECLTD.NS",
    "SIEMENS": "SIEMENS.NS",
    "TORNTPHARM": "TORNTPHARM.NS",
    "TVSMOTOR": "TVSMOTOR.NS",
    "VEDL": "VEDL.NS",
    "ZYDUSLIFE": "ZYDUSLIFE.NS"
}

# =====================================================
# SECTOR MAP
# =====================================================

SECTOR_MAP = {
    "RELIANCE": "Energy",
    "INFY": "IT",
    "TCS": "IT",
    "HDFCBANK": "Banking",
    "ICICIBANK": "Banking",
    "SBIN": "Banking",
    "BEL": "Defence",
    "HAL": "Defence",
    "TRENT": "Retail",
    "TATAMOTORS": "Auto",
    "SUNPHARMA": "Pharma",
    "AXISBANK": "Banking",
    "ITC": "FMCG",
    "LT": "Infrastructure"
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

if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = "RELIANCE"

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("📊 Watchlist")

selected_stock = st.sidebar.selectbox(
    "Search & Add Stock",
    sorted(list(NIFTY_STOCKS.keys()))
)

if st.sidebar.button("➕ Add Stock"):

    if selected_stock not in st.session_state.watchlist:
        st.session_state.watchlist.append(selected_stock)

st.sidebar.markdown("---")

stocks_to_remove = []

for stock in st.session_state.watchlist:

    col1, col2 = st.sidebar.columns([5, 1])

    with col1:

        if st.button(
            f"📌 {stock}",
            key=f"select_{stock}",
            use_container_width=True
        ):
            st.session_state.selected_stock = stock

    with col2:

        if st.button(
            "❌",
            key=f"remove_{stock}"
        ):
            stocks_to_remove.append(stock)

for stock in stocks_to_remove:

    if stock in st.session_state.watchlist:
        st.session_state.watchlist.remove(stock)

# =====================================================
# HEADER
# =====================================================

ist_time = datetime.now(ZoneInfo("Asia/Kolkata"))

col1, col2, col3 = st.columns([5, 2, 2])

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
# FETCH DATA
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
# LIVE MOMENTUM LADDER
# =====================================================

st.markdown(
    '<div class="section-title">⚡ LIVE MOMENTUM LADDER</div>',
    unsafe_allow_html=True
)

formatted_df = momentum_df.copy()

formatted_df["price"] = formatted_df["price"].map(
    "₹{:,.2f}".format
)

formatted_df["change"] = formatted_df["change"].map(
    "{:+.2f}%".format
)

formatted_df["rvol"] = formatted_df["rvol"].map(
    "{:.2f}x".format
)

formatted_df["score"] = formatted_df["score"].map(
    "{:.2f}".format
)

formatted_df["breakout"] = formatted_df["breakout"].map(
    "{:.2f}%".format
)

selected_row = st.dataframe(
    formatted_df,
    use_container_width=True,
    hide_index=False
)

# =====================================================
# HEATMAP
# =====================================================

st.markdown(
    '<div class="section-title">📈 SECTOR MOMENTUM HEATMAP</div>',
    unsafe_allow_html=True
)

sector_strength = momentum_df.groupby(
    "sector"
)["score"].mean().reset_index()

heatmap_fig = px.treemap(
    sector_strength,
    path=["sector"],
    values="score",
    color="score",
    color_continuous_scale="RdYlGn",
    custom_data=["score"]
)

heatmap_fig.update_traces(
    textfont_size=40,
    textfont_color="white",
    texttemplate="<b>%{label}</b>",
    hovertemplate="<b>%{label}</b><br>Momentum Score: %{value}<extra></extra>"
)

heatmap_fig.update_layout(
    paper_bgcolor="#0B1020",
    plot_bgcolor="#0B1020",
    font_color="white",
    height=500,
    margin=dict(t=10, l=10, r=10, b=10),
    coloraxis_showscale=False
)

st.plotly_chart(
    heatmap_fig,
    use_container_width=True
)

# =====================================================
# CHART
# =====================================================

selected_stock = st.session_state.selected_stock

if selected_stock in stock_data_map:

    chart_stock_data = stock_data_map[selected_stock]

    st.markdown(
        f'<div class="section-title">📊 {selected_stock} CHART</div>',
        unsafe_allow_html=True
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
        height=650,
        paper_bgcolor="#0B1020",
        plot_bgcolor="#0B1020",
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

st.markdown(
    '<div class="section-title">🧠 MOMENTUM INSIGHTS</div>',
    unsafe_allow_html=True
)

selected_row = momentum_df[
    momentum_df["stock"] == selected_stock
].iloc[0]

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Momentum Score",
        selected_row["score"],
        help="Overall momentum strength based on price, breakout, trend and volume activity."
    )

with col2:

    st.metric(
        "Relative Volume",
        f"{selected_row['rvol']}x",
        help="Compares current volume with average volume. Higher means stronger activity."
    )

with col3:

    st.metric(
        "Momentum State",
        selected_row["state"],
        help="Current momentum phase of the stock based on trend strength."
    )

with col4:

    st.metric(
        "Breakout Strength",
        f"{selected_row['breakout']}%",
        help="Shows how close stock is to breakout zone."
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "NSE Momentum Radar • Swing Trading Dashboard"
)
