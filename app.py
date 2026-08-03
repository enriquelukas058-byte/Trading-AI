import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import ta

st.set_page_config(page_title="Live AI Trading Analyzer", layout="wide")

st.title("🤖 Live AI Trading Analyzer Dashboard")
st.markdown("Gumagamit ng totoong live market data mula sa Yahoo Finance para sa tumpak na pagsusuri.")

st.sidebar.header("⚙️ Mga Setting ng Analisis")

# Tamang tickers para sa Yahoo Finance
symbol_option = st.sidebar.selectbox("Piliin ang Asset / Symbol", ["GC=F (Gold / XAU)", "BTC-USD (Bitcoin)", "ETH-USD (Ethereum)", "EURUSD=X (EUR/USD)", "Custom Ticker"])

if symbol_option == "Custom Ticker":
    ticker_symbol = st.sidebar.text_input("Ilagay ang Yahoo Finance Symbol (Hal: AAPL, CL=F)", value="GC=F")
else:
    ticker_symbol = symbol_option.split(" ")[0]

timeframe_map = {"5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h", "1d": "1d"}
timeframe = st.sidebar.selectbox("Timeframe", list(timeframe_map.keys()), index=3)

rsi_period = st.sidebar.slider("RSI Length", 5, 30, 14)
rr_ratio = st.sidebar.slider("Risk:Reward Ratio (TP)", 1.0, 5.0, 2.0, 0.5)

if st.sidebar.button("Suriin ang Market (Run Analysis)"):
    with st.spinner(f"Kinukuha ang totoong live data para sa {ticker_symbol}..."):
        try:
            # Kunin ang live data batay sa timeframe
            period_val = "5d" if timeframe in ["5m", "15m", "30m", "1h"] else "60d"
            df = yf.download(ticker_symbol, period=period_val, interval=timeframe_map[timeframe])
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
                
            if df.empty or len(df) < rsi_period:
                st.error("Walang sapat na live data na nakuha. Subukan ang ibang timeframe o symbol.")
            else:
                # Kalkulahin ang totoong RSI gamit ang 'ta' library
                df['RSI'] = ta.momentum.rsi(df['Close'], window=rsi_period)
                
                latest_close = float(df['Close'].iloc[-1].item())
                latest_rsi = float(df['RSI'].iloc[-1].item()) if not pd.isna(df['RSI'].iloc[-1].item()) else 50.0
                
                st.success(f"Tagumpay! Live data nakuha para sa {ticker_symbol}")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Asset", ticker_symbol)
                col2.metric("Kasalukuyang Live Presyo", f"${latest_close:,.2f}")
                col3.metric("RSI Value", f"{latest_rsi:.2f}")
                
                st.markdown("---")
                st.subheader(f"📊 Resulta ng AI Signal ({timeframe})")
                
                if latest_rsi < 45:
                    st.info(f"💡 **AI Suggestion ({timeframe}):** Oversold ang market. May potensyal na **BUY / LONG** setup.")
                elif latest_rsi > 55:
                    st.warning(f"💡 **AI Suggestion ({timeframe}):** Overbought ang market. May potensyal na **SELL / SHORT** setup.")
                else:
                    st.write(f"💡 **AI Suggestion ({timeframe}):** Neutral ang market. Maghintay ng malinaw na galaw.")

                st.markdown("---")
                st.subheader("📈 Live Price Chart")
                st.line_chart(df['Close'])
                
        except Exception as e:
            st.error(f"May naganap na error sa pagkuha ng live data: {e}")
else:
    st.info("👈 I-click ang **'Suriin ang Market'** sa sidebar para makuha ang totoong live presyo.")
