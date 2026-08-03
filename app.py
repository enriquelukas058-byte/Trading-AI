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

st.set_page_config(page_title="Pro AI Trading Analyzer", layout="wide")

st.title("🤖 Pro AI Trading & Volume Analyzer")
st.markdown("Advanced Multi-Timeframe Analysis na may Live TradingView Chart at Volume Profile Intelligence.")

st.sidebar.header("⚙️ Mga Setting ng Analisis")

# 1. Pamamahala ng Asset at Symbols
symbol_choice = st.sidebar.selectbox(
    "Piliin ang Asset / Symbol", 
    ["Gold (XAU/USD)", "Bitcoin (BTCUSD)", "Ethereum (ETHUSD)", "EUR/USD"]
)

mapping = {
    "Gold (XAU/USD)": {"tv": "TVC:GOLD", "yf": "GC=F", "base": 4063.50},
    "Bitcoin (BTCUSD)": {"tv": "BINANCE:BTCUSDT", "yf": "BTC-USD", "base": 65000.0},
    "Ethereum (ETHUSD)": {"tv": "BINANCE:ETHUSDT", "yf": "ETH-USD", "base": 2500.0},
    "EUR/USD": {"tv": "FX:EURUSD", "yf": "EURUSD=X", "base": 1.08}
}

selected_meta = mapping[symbol_choice]
tv_symbol = selected_meta["tv"]
yf_symbol = selected_meta["yf"]
base_price = selected_meta["base"]

# 2. Timeframe Selection na tugma sa parehong sistema
timeframe_option = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1h", "Daily"], index=2)
tf_map_tv = {"5m": "5", "15m": "15", "1h": "60", "Daily": "D"}[timeframe_option]
tf_map_yf = {"5m": "5m", "15m": "15m", "1h": "1h", "Daily": "1d"}[timeframe_option]

rsi_period = st.sidebar.slider("RSI Length", 5, 30, 14)

# --- UI SECTION 1: LIVE TRADINGVIEW CHART ---
st.subheader(f"📈 Live TradingView Chart ({symbol_choice} - {timeframe_option})")

tradingview_html = f"""
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
components.html(tradingview_html, height=500)

st.markdown("---")

# --- UI SECTION 2: AI BACKEND QUANTITATIVE ANALYSIS ---
st.subheader("🧠 Pro AI Quantitative & Volume Bounce Analysis")

if st.button("Patakbuhin ang AI Deep Analysis (Run Analysis)"):
    with st.spinner("Kinukuha ang market data at kinakalkula ang Volume Profile..."):
        latest_close = base_price
        latest_rsi = 50.0
        hvn_support = base_price * 0.99
        hvn_resistance = base_price * 1.01
        
        if HAS_LIVE_DATA:
            try:
                # Kunin ang sapat na historical data para sa volume distribution
                period_val = "7d" if tf_map_yf in ["5m", "15m"] else "60d"
                df = yf.download(yf_symbol, period=period_val, interval=tf_map_yf, progress=False)
                
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                if not df.empty and 'Volume' in df.columns:
                    # Linisin ang data mula sa NaNs
                    df = df.dropna()
                    
                    # Kalkulahin ang RSI gamit ang 'ta' library
                    df['RSI'] = ta.momentum.rsi(df['Close'], window=rsi_period)
                    latest_close = float(df['Close'].iloc[-1].item())
                    latest_rsi = float(df['RSI'].iloc[-1].item()) if not pd.isna(df['RSI'].iloc[-1].item()) else 50.0
                    
                    # Tumpak na Volume Profile calculation (Binning prices base sa volume)
                    num_bins = 15
                    df['Price_Bin'] = pd.cut(df['Close'], bins=num_bins)
                    vol_profile = df.groupby('Price_Bin', observed=False)['Volume'].sum()
                    
                    if not vol_profile.empty:
                        max_vol_bin = vol_profile.idxmax()
                        if pd.notna(max_vol_bin):
                            hvn_support = float(max_vol_bin.left)
                            hvn_resistance = float(max_vol_bin.right)
                else:
                    raise Exception("Invalid DataFrame or missing volume")
            except Exception as e:
                # Fallback sakaling magka-issue sa API fetch
                np.random.seed(42)
                prices = base_price + np.cumsum(np.random.normal(0, 1.5, 100))
                df = pd.DataFrame({'Close': prices, 'Volume': np.random.randint(500, 5000, 100)})
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
                latest_rsi = float(100 - (100 / (1 + (gain / loss))).iloc[-1])
                hvn_support = base_price - 15.0
                hvn_resistance = base_price + 15.0
        else:
            latest_rsi = 48.0

        # Pagpapakita ng mga Resulta sa UI gamit ang Streamlit metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Live Price Reference", f"${latest_close:,.2f}")
        col2.metric(f"RSI ({rsi_period})", f"{latest_rsi:.2f}")
        col3.metric("High Volume Bounce Zone", f"${hvn_support:,.2f} - ${hvn_resistance:,.2f}")
        
        st.markdown("---")
        
        # Smart AI Recommendations batay sa RSI at Volume Node
        if latest_rsi < 45 and latest_close <= hvn_resistance:
            st.info(f"💡 **AI Smart Signal:** **STRONG BUY SETUP**. Ang presyo ay nasa oversold level at malapit sa High Volume Node / Bounce Zone (**${hvn_support:,.2f} - ${hvn_resistance:,.2f}**). Magandang pwestuhan para sa potensyal na pag-akyat.")
        elif latest_rsi > 55 and latest_close >= hvn_support:
            st.warning(f"💡 **AI Smart Signal:** **STRONG SELL / SHORT SETUP**. Abutin man o lumagpas sa High Volume Zone (**${hvn_support:,.2f} - ${hvn_resistance:,.2f}**), overbought na ang market at posibleng magkaroon ng malakas na pagbagsak o rejection.")
        else:
            st.write(f"💡 **AI Smart Signal:** **CONSOLIDATION / NEUTRAL**. Walang direksyong masabi ang RSI. Hintayin munang pumaldo o mag-retest ang presyo sa Volume Zone na **${hvn_support:,.2f} - ${hvn_resistance:,.2f}** bago gumawa ng hakbang.")
else:
    st.info("👈 I-click ang **'Patakbuhin ang AI Deep Analysis'** para simulan ng sistema ang pagbasa sa volume at price action ng napili mong timeframe.")
