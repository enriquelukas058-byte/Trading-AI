import streamlit as st
import streamlit.components.v1 as components

# Pag-set ng page na wide
st.set_page_config(page_title="Real-Time Pro AI Trading Terminal", layout="wide")

st.title("🤖 Real-Time Pro AI Trading Terminal")
st.markdown("Live TradingView Chart kasabay ang real-time Technical Analysis meter.")

st.sidebar.header("⚙️ Mga Setting ng Analisis")

# 1. Pamamahala ng Asset at Symbols
symbol_choice = st.sidebar.selectbox(
    "Piliin ang Asset / Symbol", 
    ["Gold (XAU/USD)", "Bitcoin (BTCUSD)", "Ethereum (ETHUSD)", "EUR/USD"]
)

mapping = {
    "Gold (XAU/USD)": {"tv_chart": "TVC:GOLD", "tv_tech": "GOLD"},
    "Bitcoin (BTCUSD)": {"tv_chart": "BINANCE:BTCUSDT", "tv_tech": "BINANCE:BTCUSDT"},
    "Ethereum (ETHUSD)": {"tv_chart": "BINANCE:ETHUSDT", "tv_tech": "BINANCE:ETHUSDT"},
    "EUR/USD": {"tv_chart": "FX:EURUSD", "tv_tech": "FX:EURUSD"}
}

selected_meta = mapping[symbol_choice]
tv_symbol = selected_meta["tv_chart"]
tech_symbol = selected_meta["tv_tech"]

timeframe_option = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1h", "Daily"], index=2)
tf_map_tv = {"5m": "5", "15m": "15", "1h": "60", "Daily": "D"}[timeframe_option]
tf_map_tech = {"5m": "5m", "15m": "15m", "1h": "1h", "Daily": "1D"}[timeframe_option]

# --- SECTION 1: LIVE TRADINGVIEW CHART SA ITAAS ---
st.subheader(f"📈 Live TradingView Chart ({symbol_choice} - {timeframe_option})")

tradingview_chart_html = f"""
<div class="tradingview-widget-container" style="height:480px;width:100%">
  <div id="tradingview_chart" style="height:100%;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "width": "100%",
    "height": 480,
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
components.html(tradingview_chart_html, height=500)

st.markdown("---")

# --- SECTION 2: REAL-TIME TRADINGVIEW TECHNICAL ANALYSIS WIDGET SA IBABA ---
st.subheader(f"🧠 Real-Time AI Technical Analysis Meter para sa {symbol_choice}")
st.markdown("Ang widget na ito ay direktang kumukuha ng live indicators (RSI, MACD, Moving Averages) nang real-time mula sa TradingView.")

tradingview_analysis_html = f"""
<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
  {{
  "interval": "{tf_map_tech}",
  "width": "100%",
  "isTransparent": false,
  "height": "425",
  "symbol": "{tv_symbol}",
  "showIntervalTabs": true,
  "locale": "en",
  "colorTheme": "dark"
}}
  </script>
</div>
<!-- TradingView Widget END -->
"""

components.html(tradingview_analysis_html, height=450)
