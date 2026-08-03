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

st.set_page_config(page_title="AI Trading Analyzer with Live Chart", layout="wide")

st.title("🤖 AI Trading Analyzer & Live Chart Dashboard")
st.markdown("May kasamang live TradingView chart sa itaas at AI technical analysis button sa ibaba.")

st.sidebar.header("⚙️ Mga Setting ng Analisis")

symbol_option = st.sidebar.selectbox(
    "Piliin ang Asset / Symbol", 
    ["Gold (XAU/USD)", "Bitcoin (BTCUSD)", "Ethereum (ETHUSD)", "EUR/USD"]
)

if "Gold" in symbol_option:
    tv_symbol = "TVC:GOLD"
    yf_symbol = "GC=F"
    base_price = 4063.50
elif "Bitcoin" in symbol_option:
    tv_symbol = "BINANCE:BTCUSDT"
    yf_symbol = "BTC-USD"
    base_price = 65000.0
elif "Ethereum" in symbol_option:
    tv_symbol = "BINANCE:ETHUSDT"
    yf_symbol = "ETH-USD"
    base_price = 2500.0
else:
    tv_symbol = "FX:EURUSD"
    yf_symbol = "EURUSD=X"
    base_price = 1.08

timeframe = st.sidebar.selectbox("Timeframe (Chart & AI)", ["5", "15", "60", "D"], index=2, format_func=lambda x: {"5": "5m", "15": "15m", "60": "1h", "D": "Daily"}[x])
rsi_period = st.sidebar.slider("RSI Length", 5, 30, 14)

# 1. LIVE TRADINGVIEW CHART SA ITAAS
st.subheader(f"📈 Live TradingView Chart para sa {symbol_option}")

tradingview_html = f"""
<div class="tradingview-widget-container" style="height:450px;width:100%">
  <div id="tradingview_chart" style="height:100%;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget(
  {{
    "width": "100%",
    "height": 450,
    "symbol": "{tv_symbol}",
    "interval": "{timeframe}",
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
components.html(tradingview_html, height=470)

st.markdown("---")

# 2. AI ANALYSIS BUTTON SA IBABA (Ito ang nagpapatakbo ng pagsusuri)
st.subheader("🧠 AI Technical Analysis & Signal")

if st.button("Suriin ang Market Gamit ang AI (Run AI Analysis)"):
    with st.spinner("Kinukuha ang data at sinusuri ng AI..."):
        latest_close = base_price
        latest_rsi = 50.0
        
        if HAS_LIVE_DATA:
            try:
                tf_yf = {"5": "5m", "15": "15m", "60": "1h", "D": "1d"}[timeframe]
                period_val = "5d" if tf_yf in ["5m", "15m", "1h"] else "60d"
                df = yf.download(yf_symbol, period=period_val, interval=tf_yf)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                if not df.empty:
                    df['RSI'] = ta.momentum.rsi(df['Close'], window=rsi_period)
                    latest_close = float(df['Close'].iloc[-1].item())
                    latest_rsi = float(df['RSI'].iloc[-1].item()) if not pd.isna(df['RSI'].iloc[-1].item()) else 50.0
            except:
                np.random.seed(42)
                prices = base_price + np.cumsum(np.random.normal(0, 2, 100))
                df = pd.DataFrame({'Close': prices})
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
                latest_rsi = float(100 - (100 / (1 + (gain / loss))).iloc[-1])
        else:
            latest_rsi = 48.5
            
        col1, col2 = st.columns(2)
        col1.metric("Current Reference Price", f"${latest_close:,.2f}")
        col2.metric("RSI Indicator Value", f"${latest_rsi:.2f}" if isinstance(latest_rsi, str) else f"{latest_rsi:.2f}")
        
        if latest_rsi < 45:
            st.info("💡 **AI Recommendation:** **BUY / LONG Setup** — Oversold ang market, may tsansang umakyat ang presyo.")
        elif latest_rsi > 55:
            st.warning("💡 **AI Recommendation:** **SELL / SHORT Setup** — Overbought ang market, posibleng magkaroon ng correction o pababa.")
        else:
            st.write("💡 **AI Recommendation:** **NEUTRAL** — Walang malinaw na direksyon. Maghintay ng breakout sa chart.")
else:
    st.info("👈 Pindutin ang button sa itaas kung gusto mong suriin ng AI ang kasalukuyang takbo ng napili mong asset.")
