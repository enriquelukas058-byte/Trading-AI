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

st.set_page_config(page_title="Dual-Timeframe SMC & AI Terminal", layout="wide")

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
        font-size: 15px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Dual-Timeframe SMC & AI Trading Terminal")
st.markdown("Live TradingView Chart kasama ang hiwalay at tumpak na pagsusuri para sa **Higher Timeframe (HTF)** at **Current Timeframe (Current TF)**.")

st.sidebar.header("⚙️ Mga Setting ng Analisis")

symbol_choice = st.sidebar.selectbox(
    "Piliin ang Asset / Symbol", 
    ["Gold (XAU/USD)", "Bitcoin (BTCUSD)", "Ethereum (ETHUSD)", "EUR/USD"]
)

mapping = {
    "Gold (XAU/USD)": {"tv_chart": "TVC:GOLD", "yf": "GC=F", "base": 4068.55},
    "Bitcoin (BTCUSD)": {"tv_chart": "BINANCE:BTCUSDT", "yf": "BTC-USD", "base": 65000.0},
    "Ethereum (ETHUSD)": {"tv_chart": "BINANCE:ETHUSDT", "yf": "ETH-USD", "base": 2500.0},
    "EUR/USD": {"tv_chart": "FX:EURUSD", "yf": "EURUSD=X", "base": 1.08}
}

selected_meta = mapping[symbol_choice]
tv_symbol = selected_meta["tv_chart"]
yf_symbol = selected_meta["yf"]
base_price = selected_meta["base"]

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

# --- VARIABLES INIT ---
latest_close = base_price
htf_ob_low, htf_ob_high = base_price * 0.985, base_price * 0.992
htf_fvg_low, htf_fvg_high = base_price * 1.002, base_price * 1.008
htf_rsi = 50.0

curr_rsi = 50.0
curr_support = base_price * 0.995
curr_resistance = base_price * 1.005
curr_trend = "Neutral"

if HAS_LIVE_DATA:
    try:
        df_htf = yf.download(yf_symbol, period="5d", interval="1d", progress=False)
        if isinstance(df_htf.columns, pd.MultiIndex):
            df_htf.columns = df_htf.columns.droplevel(1)
        if not df_htf.empty:
            latest_close = float(df_htf['Close'].iloc[-1].item())
            df_htf['RSI'] = ta.momentum.rsi(df_htf['Close'], window=14)
            htf_rsi = float(df_htf['RSI'].iloc[-1].item()) if not pd.isna(df_htf['RSI'].iloc[-1].item()) else 50.0
            
            htf_low = float(df_htf['Low'].tail(15).min())
            htf_high = float(df_htf['High'].tail(15).max())
            htf_ob_low, htf_ob_high = htf_low, htf_low + (htf_high - htf_low) * 0.30
            htf_fvg_low, htf_fvg_high = htf_high - (htf_high - htf_low) * 0.30, htf_high

        df_curr = yf.download(yf_symbol, period="5d", interval=tf_map_yf, progress=False)
        if isinstance(df_curr.columns, pd.MultiIndex):
            df_curr.columns = df_curr.columns.droplevel(1)
        if not df_curr.empty and len(df_curr) > 14:
            curr_rsi = float(ta.momentum.rsi(df_curr['Close'], window=14).iloc[-1].item())
            curr_support = float(df_curr['Low'].tail(5).min())
            curr_resistance = float(df_curr['High'].tail(5).max())
            
            sma_s = df_curr['Close'].rolling(window=5).mean().iloc[-1]
            sma_l = df_curr['Close'].rolling(window=15).mean().iloc[-1]
            curr_trend = "Bullish (Umakyat)" if sma_s > sma_l else "Bearish (Bumaba)"
    except:
        pass

# --- SEKSYON A: HIGHER TIMEFRAME (HTF - DAILY) ANALYSIS ---
st.markdown("### 🏛️ 1. Higher Timeframe (HTF - Daily) Analysis")
st.markdown("Ginagamit para malaman ang malaking takbo ng merkado, pangunahing Order Blocks, at Fair Value Gaps.")

ac1, ac2, ac3, ac4 = st.columns(4)
with ac1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Market Price</div><div class="metric-value">${latest_close:,.2f}</div></div>', unsafe_allow_html=True)
with ac2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">HTF Order Block (POI)</div><div class="metric-value" style="color: #48bb78;">${htf_ob_low:,.2f} - ${htf_ob_high:,.2f}</div></div>', unsafe_allow_html=True)
with ac3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">HTF Fair Value Gap</div><div class="metric-value" style="color: #ecc94b;">${htf_fvg_low:,.2f} - ${htf_fvg_high:,.2f}</div></div>', unsafe_allow_html=True)
with ac4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">HTF Daily RSI</div><div class="metric-value">{htf_rsi:.1f}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if latest_close <= htf_ob_high:
    st.success(f"💡 **HTF Recommendation:** Ang presyo ay nasa Daily Order Block zone (**${htf_ob_low:,.2f} - ${htf_ob_high:,.2f}**). May mataas na tsansa ng **Long-term Buy / Rebound** sa Higher Timeframe.")
elif latest_close >= htf_fvg_low:
    st.warning(f"💡 **HTF Recommendation:** Ang presyo ay umabot na sa Daily FVG / Resistance zone (**${htf_fvg_low:,.2f} - ${htf_fvg_high:,.2f}**). Mag-ingat sa pag-akyat; asahan ang posibleng **HTF Correction o Short**.")
else:
    st.info(f"💡 **HTF Recommendation:** Nasa gitna ng Daily range ang presyo. Hintayin itong lumapit sa Order Block sa **${htf_ob_low:,.2f}** para sa ligtas na pwesto.")

st.markdown("---")

# --- SEKSYON B: CURRENT TIMEFRAME ANALYSIS ---
st.markdown(f"### ⚡ 2. Current Timeframe ({timeframe_option}) Analysis")
st.markdown(f"Ginagamit para sa mabilisang desisyon, short-term support/resistance, at entry sa mismong {timeframe_option} chart.")

bc1, bc2, bc3, bc4 = st.columns(4)
with bc1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Active Timeframe</div><div class="metric-value">{timeframe_option}</div></div>', unsafe_allow_html=True)
with bc2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Current TF Support</div><div class="metric-value" style="color: #48bb78;">${curr_support:,.2f}</div></div>', unsafe_allow_html=True)
with bc3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Current TF Resistance</div><div class="metric-value" style="color: #f56565;">${curr_resistance:,.2f}</div></div>', unsafe_allow_html=True)
with bc4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Current TF RSI & Trend</div><div class="metric-value">{curr_rsi:.1f} ({curr_trend})</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if curr_rsi < 40:
    st.success(f"💡 **Current TF ({timeframe_option}) Recommendation:** Oversold ang RSI ({curr_rsi:.1f}) sa {timeframe_option}. Magandang pwestuhan ang malapit sa Support (${curr_support:,.2f}) para sa **Short-term Buy / Scalp** pabalik sa resistance.")
elif curr_rsi > 60:
    st.warning(f"💡 **Current TF ({timeframe_option}) Recommendation:** Overbought ang RSI ({curr_rsi:.1f}) sa {timeframe_option}. Malapit na sa Resistance (${curr_resistance:,.2f}), kaya mainam mag-abang ng **Short-term Sell / Pullback**.")
else:
    st.info(f"💡 **Current TF ({timeframe_option}) Recommendation:** Neutral ang RSI ({curr_rsi:.1f}) sa {timeframe_option}. Walang malinaw na mabilisang galaw; abangan kung ma-break ang support o resistance.")
