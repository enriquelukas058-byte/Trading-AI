# 1. Kunin ang HTF (Daily) Data at Live Price
        df_htf = yf.download(yf_symbol, period="5d", interval="1d", progress=False)
        if isinstance(df_htf.columns, pd.MultiIndex):
            df_htf.columns = df_htf.columns.droplevel(1)
        if not df_htf.empty:
            # Kunin ang pinakabagong live close price mula sa Daily/Market feed
            latest_close = float(df_htf['Close'].iloc[-1].item())
