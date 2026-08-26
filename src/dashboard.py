import streamlit as st
import pandas as pd
from datetime import datetime
import ollama
import yfinance as yf

# 1. Page Configuration
st.set_page_config(page_title="AI Market Agent", layout="wide")
st.title("📈 AI-Powered Portfolio Dashboard")
st.markdown("Select an equity from your portfolio to view its 30-day price action, live earnings data, and generate an AI summary.")

# 2. Master Portfolio Tickers
TICKERS = [
    "MSFT", "CRWD", "AVGO", "GLE.PA", "NVDA", "AMZN", "AXON", "PANW", 
    "INTC", "NOW", "IREN", "GOOG", "MU", "SOFI", "PLTR", "RDW", "DRAM"
]

selected_ticker = st.selectbox("Select a Stock to Analyze:", TICKERS)

# 3. Load Local CSV Data Safely
today_str = datetime.now().strftime('%Y%m%d')
file_path = f"data/raw/{selected_ticker}_raw_{today_str}.csv"

try:
    # Read raw CSV and handle yfinance headers
    df = pd.read_csv(file_path)
    if 'Price' in df.columns or 'Ticker' in df.columns or 'Unnamed' in str(df.columns[0]):
        df = pd.read_csv(file_path, skiprows=3, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
    
    # Clean up types for charting
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df = df.dropna(subset=['Close'])

    # 4. Display Price Chart
    st.subheader(f"{selected_ticker} - 30 Day Price Trend")
    st.line_chart(df.set_index('Date')['Close'])
    
    st.divider()
    
    # 5. Live Earnings Section
    st.subheader(f"📊 {selected_ticker} Live Earnings Report & Expectations")
    
    with st.spinner("Fetching live earnings data..."):
        ticker_data = yf.Ticker(selected_ticker)
        try:
            earnings_dates = ticker_data.get_earnings_dates(limit=4)
            if earnings_dates is not None and not earnings_dates.empty:
                earnings_dates.index = earnings_dates.index.tz_localize(None)
                st.dataframe(earnings_dates[['EPS Estimate', 'Reported EPS', 'Surprise(%)']])
            else:
                st.info("No recent earnings surprise data available.")
        except Exception:
            st.info("Earnings calendar currently unavailable for this ticker.")
                
    st.divider()

    # 6. Local AI Analyst Summary
    st.subheader("Wall Street Analyst Summary")
    if st.button(f"Generate Insights for {selected_ticker}"):
        with st.spinner("Analyzing data with local Llama 3..."):
            recent_data = df.tail(5)
            trend_text = recent_data.to_string(index=False)
            
            prompt = f"""
            You are a Senior Equity Research Analyst at a top-tier Wall Street investment bank. 
            Review the following 5-day trailing market data for {selected_ticker}:
            {trend_text}
            
            Provide a concise, 2-sentence market update suitable for an institutional morning briefing. 
            Focus on price action, momentum, and technical sentiment. 
            Use professional financial terminology.
            """

            response = ollama.chat(model='llama3', messages=[
                {"role": "system", "content": "You are a Wall Street Equity Research Analyst."},
                {"role": "user", "content": prompt}
            ])
            
            st.success("Analysis Complete!")
            if isinstance(response, dict):
                st.write(response['message']['content'])
            else:
                st.write(response.message.content)

except FileNotFoundError:
    st.error(f"No local data found for {selected_ticker}. Run 'python src/fetch_market_data.py' to update your local store.")
