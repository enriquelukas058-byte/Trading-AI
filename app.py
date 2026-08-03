import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Pro AI Trading Terminal with Analysis Boxes", layout="wide")

st.markdown("""
    <style>
    .metric-card {
        background-color: #1e2530;
        border: 1px solid #2d3748;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        color: #a0aec0;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Pro AI Trading Terminal & Analysis Boxes")
st.markdown("Live TradingView Chart sa itaas, kasama ang Real-Time Technical Analysis Meter at mga pagsusuri sa ibaba.")

st.sidebar.header("⚙️ Mga Setting ng Analisis")

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

timeframe_option = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1h", "Daily"], index=2)
tf_map_tv = {"5m": "5", "15m": "15", "1h": "60", "Daily": "D"}[timeframe_option]
tf_map_tech = {"5m": "5m", "15m": "15m", "1h": "1h", "Daily": "1D"}[timeframe_option]

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

# --- SECTION 2: AI ANALYSIS BOXES & REAL-TIME METER SA IBABA ---
st.subheader(f"🧠 Real-Time AI Technical Analysis & Market Summary para sa {symbol_choice}")

# Mga Kahon para sa mabilisang impormasyon at gabay
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Timeframe</div>
            <div class="metric-value">{timeframe_option}</div>
        </div>
    """, unsafe_allow_html=True)
    
with c2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Target Asset</div>
            <div class="metric-value">{symbol_choice}</div>
        </div>
    """, unsafe_allow_html=True)
    
with c3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Analysis Engine</div>
            <div class="metric-value" style="color: #48bb78;">Live TradingView Feed</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Opisyal at Real-Time na Technical Analysis Meter mula sa TradingView
tradingview_analysis_html = f"""
<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
  {{
  "interval": "{tf_map_tech}",
  "width": "100%",
  "isTransparent": false,
  "height": "400",
  "symbol": "{tv_symbol}",
  "showIntervalTabs": true,
  "locale": "en",
  "colorTheme": "dark"
}}
  </script>
</div>
<!-- TradingView Widget END -->
"""

components.html(tradingview_analysis_html, height=420)
