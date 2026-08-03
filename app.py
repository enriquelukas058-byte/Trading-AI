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

st.set_page_config(page_title="Pro Smart Money Concepts (SMC) Terminal", layout="wide")

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
        font-size: 18px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Pro SMC & HTF Analysis Terminal (POI, FVG, OB)")
st.markdown("Live TradingView Chart kasama ang Smart Money Concepts (Order Blocks, Fair Value Gaps, at Price Recommendations).")

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

timeframe_option = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1h", "Daily"], index=2)
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

# --- SECTION 2: HTF SMC ANALYSIS & PRICE RECOMMENDATIONS ---
st.subheader(f"🧠 Smart Money Concepts (HTF POI, FVG, OB) para sa {symbol_choice}")

latest_close = base_price
ob_zone_low = base_price * 0.985
ob_zone_high = base_price * 0.992
fvg_low = base_price * 1.002
fvg_high = base_price * 1.008
rsi_val = 50.0

if HAS_LIVE_DATA:
    try:
        df = yf.download(yf_symbol, period="30d", interval=tf_map_yf, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        if not df.empty:
            latest_close = float(df['Close'].iloc[-1].item())
            # Kalkulahin ang RSI para sa kumpirmasyon
            df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
            rsi_val = float(df['RSI'].iloc[-1].item()) if not pd.isna(df['RSI'].iloc[-1].item()) else 50.0
            
            # Pagtantiya ng Order Block (OB) at Fair Value Gap (FVG) base sa huling galaw
            recent_low = float(df['Low'].tail(10).min())
            recent_high = float(df['High'].tail(10).max())
            ob_zone_low = recent_low
            ob_zone_high = recent_low + (recent_high - recent_low) * 0.35
            fvg_low = recent_high - (recent_high - recent_low) * 0.35
            fvg_high = recent_high
    except:
        pass

# Pagpapakita ng mga Presyo at SMC Zones sa mga kahon
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
            <div class="metric-title">Order Block (OB / POI)</div>
            <div class="metric-value" style="font-size: 15px; color: #48bb78;">${ob_zone_low:,.2f} - ${ob_zone_high:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Fair Value Gap (FVG)</div>
            <div class="metric-value" style="font-size: 15px; color: #ecc94b;">${fvg_low:,.2f} - ${fvg_high:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">RSI (14) Momentum</div>
            <div class="metric-value">{rsi_val:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Direktang Rekomendasyon at Price Action Analysis
if latest_close <= ob_zone_high:
    st.success(f"💡 **SMC Buy Recommendation:** Ang presyo ay kasalukuyang pumapasok sa **Order Block / POI Zone** na **${ob_zone_low:,.2f} - ${ob_zone_high:,.2f}**. Magandang abangan ang bullish rejection para sa posibleng **BUY / LONG** entry na may Stop Loss sa ibaba ng zone na ito.")
elif latest_close >= fvg_low:
    st.warning(f"💡 **SMC Sell / Rejection Recommendation:** Ang presyo ay lumapit o nasa loob na ng **Fair Value Gap / Resistance Zone** na **${fvg_low:,.2f} - ${fvg_high:,.2f}**. Mag-ingat sa pagbili dito; posibleng magkaroon ng correction o **SELL / SHORT** setup.")
else:
    st.info(f"💡 **SMC Neutral / Waiting Zone:** Nasa gitna ng saklaw ang presyo. Hintayin munang bumaba ang presyo pabalik sa **OB Zone (${ob_zone_low:,.2f})** para sa ligtas na pag-abang ng buy setup.")
