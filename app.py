import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import yfinance as yf
except ImportError:
    install("yfinance")
    import yfinance as yf

try:
    import ta
except ImportError:
    install("ta")
    import ta

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Trading Analyzer [RSI & SMC Logic]", layout="wide")

st.title("🤖 AI Trading Analyzer Dashboard")
st.markdown("Isang Python web app na gumagamit ng RSI Crossover, ATR Risk Management, at Trend Analysis para sa iyong trading.")

st.sidebar.header("⚙️ Mga Setting ng Analisis")
ticker_symbol = st.sidebar.text_input("Ilagay ang Ticker / Symbol (Halimbawa: BTC-USD, ETH-USD, AAPL)", value="BTC-USD")
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "1d"], index=0)
rsi_period = st.sidebar.slider("RSI Length", 5, 30, 14)
atr_mult = st.sidebar.slider("ATR Multiplier (Stop Loss)", 0.5, 3.0, 1.5, 0.1)
rr_ratio = st.sidebar.slider("Risk:Reward Ratio (TP)", 1.0, 5.0, 2.0, 0.5)

if st.sidebar.button("Suriin ang Market (Run Analysis)"):
    with st.spinner(f"Kinukuha ang data para sa {ticker_symbol}..."):
        try:
            period_val = "60d" if timeframe == "1h" else "1y"
            df = yf.download(ticker_symbol, period=period_val, interval=timeframe)
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
                
            if df.empty:
                st.error("Walang nakuhang data. Pakitingnan kung tama ang ticker symbol.")
            else:
                df['RSI'] = ta.momentum.rsi(df['Close'], window=rsi_period)
                df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
                
                latest_close = float(df['Close'].iloc[-1])
                latest_rsi = float(df['RSI'].iloc[-1])
                latest_atr = float(df['ATR'].iloc[-1])
                
                buy_sl = latest_close - (latest_atr * atr_mult)
                buy_tp = latest_close + ((latest_close - buy_sl) * rr_ratio)
                
                sell_sl = latest_close + (latest_atr * atr_mult)
                sell_tp = latest_close - ((sell_sl - latest_close) * rr_ratio)
                
                st.success(f"Tagumpay! Nasuri na ang {ticker_symbol}")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Kasalukuyang Presyo", f"${latest_close:,.2f}")
                col2.metric("RSI Value", f"{latest_rsi:.2f}")
                col3.metric("ATR (Volatility)", f"{latest_atr:.2f}")
                
                st.markdown("---")
                st.subheader("📊 Resulta ng AI Signal at Risk Management")
                
                if latest_rsi < 45:
                    st.info("💡 **AI Suggestion:** Oversold ang market. May potensyal na **BUY / LONG** setup kung aakyat ang presyo.")
                    st.write(f"* **Inirerekumendang Stop Loss (SL):** `${buy_sl:,.2f}`")
                    st.write(f"* **Inirerekumendang Take Profit (TP):** `${buy_tp:,.2f}`")
                elif latest_rsi > 55:
                    st.warning("💡 **AI Suggestion:** Overbought ang market. May potensyal na **SELL / SHORT** setup kung hihina ang presyo.")
                    st.write(f"* **Inirerekumendang Stop Loss (SL):** `${sell_sl:,.2f}`")
                    st.write(f"* **Inirerekumendang Take Profit (TP):** `${sell_tp:,.2f}`")
                else:
                    st.write("💡 **AI Suggestion:** Neutral ang market. Maghintay ng malinaw na breakout o signal bago pumasok.")

                st.markdown("---")
                st.subheader("📈 Price Chart")
                st.line_chart(df['Close'])
                
        except Exception as e:
            st.error(f"May naganap na error: {e}")
else:
    st.info("👈 I-click ang **'Suriin ang Market'** sa sidebar para simulan ang pagsusuri.")
