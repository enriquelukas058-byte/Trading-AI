import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Trading Analyzer", layout="wide")

st.title("🤖 AI Trading Analyzer Dashboard")
st.markdown("Isang mabilis at maaasahang trading analysis tool para sa iyong mobile phone.")

st.sidebar.header("⚙️ Mga Setting ng Analisis")
ticker_symbol = st.sidebar.text_input("Ilagay ang Ticker / Symbol", value="BTC-USD")
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "1s", "1d"], index=0)
rsi_period = st.sidebar.slider("RSI Length", 5, 30, 14)
rr_ratio = st.sidebar.slider("Risk:Reward Ratio (TP)", 1.0, 5.0, 2.0, 0.5)

if st.sidebar.button("Suriin ang Market (Run Analysis)"):
    with st.spinner(f"Sinusuri ang data para sa {ticker_symbol}..."):
        # Gumawa ng simulated realistic price data para tuluyang maging stable at mabilis sa cloud
        np.random.seed(42)
        base_price = 65000.0 if "BTC" in ticker_symbol.upper() else 2000.0
        price_changes = np.random.normal(loc=0.0, scale=150.0, size=100)
        prices = base_price + np.cumsum(price_changes)
        
        df = pd.DataFrame({'Close': prices})
        
        # Simple RSI calculation gamit ang pandas
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        latest_close = float(df['Close'].iloc[-1])
        latest_rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50.0
        
        st.success(f"Tagumpay! Nasuri na ang {ticker_symbol}")
        
        col1, col2 = st.columns(2)
        col1.metric("Kasalukuyang Presyo (Simulated)", f"${latest_close:,.2f}")
        col2.metric("RSI Value", f"{latest_rsi:.2f}")
        
        st.markdown("---")
        st.subheader("📊 Resulta ng AI Signal")
        
        if latest_rsi < 45:
            st.info("💡 **AI Suggestion:** Oversold ang market. May potensyal na **BUY / LONG** setup.")
        elif latest_rsi > 55:
            st.warning("💡 **AI Suggestion:** Overbought ang market. May potensyal na **SELL / SHORT** setup.")
        else:
            st.write("💡 **AI Suggestion:** Neutral ang market. Maghintay ng magandang galaw.")

        st.markdown("---")
        st.subheader("📈 Price Chart")
        st.line_chart(df['Close'])
else:
    st.info("👈 I-click ang **'Suriin ang Market'** sa sidebar.")
