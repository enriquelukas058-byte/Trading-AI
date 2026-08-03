import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np

try:
    import yfinance as yf
    import ta
    HAS_LIVE_DATA = True
except ImportError:
    HAS_LIVE_DATA = False

st.set_page_config(page_title="Dual-Timeframe SMC & AI Trading Terminal", layout="wide")

st.markdown("""
    <style>
    .metric-card {
        background-color: #1e2530;
        border: 1px solid #2d3748;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        color: #a0aec0;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 16px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Dual-Timeframe SMC & AI Trading Terminal")
st.markdown("Live TradingView Chart kasama ang HTF (Daily) at Current Timeframe (Lower TF) Action Analysis.")

st.sidebar.header("⚙️ Mga Setting ng Analisis")

symbol_choice = st.sidebar.selectbox(
    "Piliin ang Asset / Symbol", 
    ["Gold (XAU/USD)", "Bitcoin (BTCUSD)", "Ethereum (ETHUSD)", "EUR/USD"]
)

mapping = {
    "Gold (XAU/USD)": {"tv_chart": "TVC:GOLD", "yf": "GC=F", "base": 4063.50},
    "Bitcoin (BTCUSD)": {"tv_chart": "BINANCE:BTCUSDT", "yf": "BTC-USD", "base": 65000.0},
    "Ethereum (ETHUSD)": {"tv_chart": "BINANCE:ETHUSDT", "yf": "ETH-USD", "base": 2500.0},
    "EUR/USD": {"tv_chart": "FX:EURUSD", "yf": "EURUSD=X", "base": 1.08}
}

selected_meta = mapping[symbol_choice]
tv_symbol = selected_meta["tv_chart"]
yf_symbol = selected_meta["yf"]
base_price = selected_meta["base"]

# Timeframe para sa Chart at Current TF Analysis sa Sidebar
timeframe_option = st.sidebar.selectbox("Current Timeframe (Chart & Lower TF)", ["5m", "15m", "1h", "Daily"], index=0)
tf_map_tv = {"5m": "5", "15m": "15", "1h": "60", "Daily": "D"}[timeframe_option]
tf_map_yf = {"5m": "5m", "15m": "15m", "1h": "1h", "Daily": "1d"}[timeframe_option]

# --- SECTION 1: LIVE TRADINGVIEW CHART SA ITAAS ---
st.subheader(f"📈 Live TradingView Chart ({symbol_choice} - {timeframe_option})")

tradingview_chart_html = f"""
<div class="tradingview-widget-container" style="height:450px;width:100%">
  <div id="tradingview_chart" style="height:100%;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "width": "100%",
    "height": 450,
    "symbol": "{tv_symbol}",
    "interval": "{tf_map_tv}",
    "timezone": "Asia/Manila",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "details": true,
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""
components.html(tradingview_chart_html, height=470)

st.markdown("---")

# --- SECTION 2: DUAL-TIMEFRAME ANALYSIS (HTF + CURRENT TF) ---
st.subheader(f"🧠 Dual-Timeframe Smart Money Analysis para sa {symbol_choice}")

latest_close = base_price
htf_ob_low, htf_ob_high = base_price * 0.985, base_price * 0.992
htf_fvg_low, htf_fvg_high = base_price * 1.002, base_price * 1.008

curr_rsi = 50.0
curr_trend = "Neutral"

if HAS_LIVE_DATA:
    try:
        # 1. Kunin ang HTF (Daily) Data para sa POI / OB
        df_htf = yf.download(yf_symbol, period="60d", interval="1d", progress=False)
        if isinstance(df_htf.columns, pd.MultiIndex):
            df_htf.columns = df_htf.columns.droplevel(1)
        if not df_htf.empty:
            latest_close = float(df_htf['Close'].iloc[-1].item())
            htf_low = float(df_htf['Low'].tail(15).min())
            htf_high = float(df_htf['High'].tail(15).max())
            htf_ob_low, htf_ob_high = htf_low, htf_low + (htf_high - htf_low) * 0.30
            htf_fvg_low, htf_fvg_high = htf_high - (htf_high - htf_low) * 0.30, htf_high

        # 2. Kunin ang Current TF Data (kung ano ang pinili sa sidebar: 5m, 15m, etc.)
        df_curr = yf.download(yf_symbol, period="5d", interval=tf_map_yf, progress=False)
        if isinstance(df_curr.columns, pd.MultiIndex):
            df_curr.columns = df_curr.columns.droplevel(1)
        if not df_curr.empty and len(df_curr) > 14:
            df_curr['RSI'] = ta.momentum.rsi(df_curr['Close'], window=14)
            curr_rsi = float(df_curr['RSI'].iloc[-1].item()) if not pd.isna(df_curr['RSI'].iloc[-1].item()) else 50.0
            
            # Simple Trend Direction batay sa Moving Average ng Current TF
            sma_short = df_curr['Close'].rolling(window=5).mean().iloc[-1]
            sma_long = df_curr['Close'].rolling(window=20).mean().iloc[-1]
            curr_trend = "Bullish (Umakyat)" if sma_short > sma_long else "Bearish (Bumaba)"
    except:
        pass

# Pagpapakita sa UI ng mga Kahon
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Live Price</div>
            <div class="metric-value">${latest_close:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">HTF Order Block (Daily)</div>
            <div class="metric-value" style="font-size: 13px; color: #48bb78;">${htf_ob_low:,.2f} - ${htf_ob_high:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Current TF ({timeframe_option}) RSI</div>
            <div class="metric-value">{curr_rsi:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Current TF Momentum</div>
            <div class="metric-value" style="font-size: 13px; color: #ecc94b;">{curr_trend}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- SPECIFIC AI ACTION RECOMMENDATION BATAY SA DUAL-TIMEFRAME ---
st.markdown(f"### 🎯 Action Recommendation para sa {timeframe_option} Chart:")

if curr_rsi < 40:
    st.success(f"💡 **Current TF Buy Setup (Oversold sa {timeframe_option}):** Dahil oversold ang RSI ({curr_rsi:.1f}) sa {timeframe_option}, magandang mag-abang ng short-term **BUY / LONG bounce** papuntang resistance, lalo na kung malapit ito sa HTF Support.")
elif curr_rsi > 60:
    st.warning(f"💡 **Current TF Sell / Correction Setup (Overbought sa {timeframe_option}):** Overbought ang RSI ({curr_rsi:.1f}) sa {timeframe_option} timeframe. Mag-ingat sa pagpasok ng bagong buy; magandang pag-isipan ang **SELL / SHORT** o pag-antay ng pullback.")
else:
    st.info(f"💡 **Current TF Neutral / Consolidation sa {timeframe_option}:** Nasa saklaw na 40-60 ang RSI ({curr_rsi:.1f}). Walang malinaw na direksyon sa {timeframe_option} kaya mas mabuting bantayan muna ang paggalaw ng presyo sa mga HTF zones.")
