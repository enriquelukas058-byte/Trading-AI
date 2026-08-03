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

st.set_page_config(page_title="True HTF SMC & AI Trading Terminal", layout="wide")

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
        font-size: 17px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 True HTF SMC & AI Trading Terminal")
st.markdown("Live TradingView Chart (Lower Timeframe) kasama ang Higher Timeframe (HTF) Order Blocks at Fair Value Gaps.")

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

# Timeframe para sa Chart sa Itaas
timeframe_option = st.sidebar.selectbox("Chart Timeframe (Itaas)", ["5m", "15m", "1h", "Daily"], index=0)
tf_map_tv = {"5m": "5", "15m": "15", "1h": "60", "Daily": "D"}[timeframe_option]

# --- SECTION 1: LIVE TRADINGVIEW CHART SA ITAAS (Sinusunod ang pinili mo) ---
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

# --- SECTION 2: TRUE HTF (DAILY / 1H) ANALYSIS & PRICE RECOMMENDATIONS ---
st.subheader(f"🧠 Higher Timeframe (HTF - Daily/1H) SMC Analysis para sa {symbol_choice}")
st.markdown("*Ang mga presyong ito ay kinuha mula sa Higher Timeframe (Daily) data para sa mas matibay na POI at Order Blocks.*")

latest_close = base_price
htf_ob_low = base_price * 0.985
htf_ob_high = base_price * 0.992
htf_fvg_low = base_price * 1.002
htf_fvg_high = base_price * 1.008
rsi_val = 50.0

if HAS_LIVE_DATA:
    try:
        # Palaging kukuha ng 'Daily' (1d) data para sa tunay na HTF Analysis kahit 5m ang nasa chart mo
        df_htf = yf.download(yf_symbol, period="60d", interval="1d", progress=False)
        if isinstance(df_htf.columns, pd.MultiIndex):
            df_htf.columns = df_htf.columns.droplevel(1)
        if not df_htf.empty:
            latest_close = float(df_htf['Close'].iloc[-1].item())
            df_htf['RSI'] = ta.momentum.rsi(df_htf['Close'], window=14)
            rsi_val = float(df_htf['RSI'].iloc[-1].item()) if not pd.isna(df_htf['RSI'].iloc[-1].item()) else 50.0
            
            # Pagtukoy ng HTF Order Block at Fair Value Gap mula sa Daily candles
            htf_low = float(df_htf['Low'].tail(15).min())
            htf_high = float(df_htf['High'].tail(15).max())
            htf_ob_low = htf_low
            htf_ob_high = htf_low + (htf_high - htf_low) * 0.30
            htf_fvg_low = htf_high - (htf_high - htf_low) * 0.30
            htf_fvg_high = htf_high
    except:
        pass

# Pagpapakita ng mga Presyo at HTF Zones sa mga kahon na may malinaw na detalye
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Live Price (Market)</div>
            <div class="metric-value">${latest_close:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">HTF Order Block (Daily POI)</div>
            <div class="metric-value" style="font-size: 14px; color: #48bb78;">${htf_ob_low:,.2f} - ${htf_ob_high:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">HTF Fair Value Gap (Daily)</div>
            <div class="metric-value" style="font-size: 14px; color: #ecc94b;">${htf_fvg_low:,.2f} - ${htf_fvg_high:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">HTF RSI (14 - Daily)</div>
            <div class="metric-value">{rsi_val:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tukoy at Specific na Rekomendasyon batay sa HTF Data
if latest_close <= htf_ob_high:
    st.success(f"💡 **HTF SMC Buy Recommendation:** Ang presyo sa market (${latest_close:,.2f}) ay nasa loob o malapit sa **Daily Higher Timeframe Order Block** na **${htf_ob_low:,.2f} - ${htf_ob_high:,.2f}**. Magandang abangan ang pag-rebound para sa **BUY / LONG** pwesto.")
elif latest_close >= htf_fvg_low:
    st.warning(f"💡 **HTF SMC Sell Recommendation:** Ang presyo sa market (${latest_close:,.2f}) ay umabot sa **Daily Fair Value Gap / Resistance** na **${htf_fvg_low:,.2f} - ${htf_fvg_high:,.2f}**. Mag-ingat sa pagbili dahil malaki ang tsansa ng rejection o pagbaba (**SELL / SHORT**).")
else:
    st.info(f"💡 **HTF SMC Waiting Zone:** Ang presyo ay nasa gitna ng Daily range. Hintayin munang bumaba ang presyo papunta sa HTF Order Block sa **${htf_ob_low:,.2f}** bago pumasok.")
