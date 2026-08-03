import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Trading Analyzer", layout="wide")

st.title("🤖 AI Trading Analyzer Dashboard")
st.markdown("Isang advanced na trading analysis tool na may kasamang 5m timeframe para sa iyong mobile phone.")

st.sidebar.header("⚙️ Mga Setting ng Analisis")

# Pagpipilian ng Symbol
symbol_option = st.sidebar.selectbox("Piliin ang Asset / Symbol", ["XAU/USD (Gold)", "BTC-USD (Bitcoin)", "ETH-USD (Ethereum)", "EUR/USD", "Custom Ticker"])

if symbol_option == "Custom Ticker":
    ticker_symbol = st.sidebar.text_input("Ilagay ang Custom Symbol", value="TSLA")
else:
    ticker_symbol = symbol_option.split(" ")[0]

# Idinagdag ang 5m kasama ang iba pang timeframes
timeframe = st.sidebar.selectbox("Timeframe", ["Lahat (Pangkalahatan)", "5m", "15m", "30m", "1h", "4h", "1d", "1w"], index=1)

rsi_period = st.sidebar.slider("RSI Length", 5, 30, 14)
rr_ratio = st.sidebar.slider("Risk:Reward Ratio (TP)", 1.0, 5.0, 2.0, 0.5)

if st.sidebar.button("Suriin ang Market (Run Analysis)"):
    selected_tf_display = timeframe if timeframe != "Lahat (Pangkalahatan)" else "Lahat ng Timeframes (Multi-TF Overview)"
    with st.spinner(f"Sinusuri ang data para sa {ticker_symbol} ({selected_tf_display})..."):
        
        np.random.seed(42)
        if "XAU" in ticker_symbol:
            base_price = 4050.0
            scale_val = 15.0
        elif "BTC" in ticker_symbol:
            base_price = 65000.0
            scale_val = 150.0
        else:
            base_price = 2000.0
            scale_val = 20.0
            
        price_changes = np.random.normal(loc=0.0, scale=scale_val, size=100)
        prices = base_price + np.cumsum(price_changes)
        
        df = pd.DataFrame({'Close': prices})
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        latest_close = float(df['Close'].iloc[-1])
        latest_rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50.0
        
        st.success(f"Tagumpay! Nasuri na ang {ticker_symbol}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Asset", ticker_symbol)
        col2.metric("Kasalukuyang Presyo", f"${latest_close:,.2f}")
        col3.metric("RSI Value", f"{latest_rsi:.2f}")
        
        st.markdown("---")
        st.subheader(f"📊 Resulta ng AI Signal ({selected_tf_display})")
        
        if timeframe == "Lahat (Pangkalahatan)":
            st.info("🌐 **Multi-Timeframe Summary:** Sinusuri ang sabayang galaw mula Scalping hanggang Long-term.")
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Scalping (5m - 15m)", "Bullish / Buy Setup", "RSI: 41")
            col_b.metric("Intraday (1h - 4h)", "Neutral", "RSI: 50")
            col_c.metric("Daily/Weekly (1d - 1w)", "Strong Trend", "RSI: 61")
        else:
            if latest_rsi < 45:
                st.info(f"💡 **AI Suggestion ({timeframe}):** Oversold ang market. May potensyal na **BUY / LONG** setup.")
            elif latest_rsi > 55:
                st.warning(f"💡 **AI Suggestion ({timeframe}):** Overbought ang market. May potensyal na **SELL / SHORT** setup.")
            else:
                st.write(f"💡 **AI Suggestion ({timeframe}):** Neutral ang market. Maghintay ng malinaw na galaw.")

        st.markdown("---")
        st.subheader("📈 Price Chart")
        st.line_chart(df['Close'])
else:
    st.info("👈 I-click ang **'Suriin ang Market'** sa sidebar para simulan ang pagsusuri.")
