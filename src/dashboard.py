import streamlit as st
import pandas as pd
from datetime import datetime
import ollama
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Page Configuration (No emojis, sleek layout)
st.set_page_config(page_title="Institutional Portfolio Dashboard", layout="wide")
st.title("INSTITUTIONAL PORTFOLIO DASHBOARD")
st.markdown("Select a security from your portfolio to view market action, detailed financials, and generate an AI-driven briefing.")

# 2. Master Portfolio Tickers
TICKERS = [
    "MSFT", "CRWD", "AVGO", "GLE.PA", "NVDA", "AMZN", "AXON", "PANW", 
    "INTC", "NOW", "IREN", "GOOG", "MU", "SOFI", "PLTR", "RDW", "DRAM"
]

selected_ticker = st.selectbox("Select Security:", TICKERS)

# 3. Load Local CSV Data Safely for Charting
today_str = datetime.now().strftime('%Y%m%d')
file_path = f"data/raw/{selected_ticker}_raw_{today_str}.csv"

try:
    # Read raw CSV and handle yfinance headers
    df = pd.read_csv(file_path)
    if 'Price' in df.columns or 'Ticker' in df.columns or 'Unnamed' in str(df.columns[0]):
        df = pd.read_csv(file_path, skiprows=3, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
    
    # Clean up types for charting
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Close', 'Date'])
    
    # Calculate Moving Averages (20-day and 50-day)
    df['SMA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()
    df['SMA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()

    # 4. Display Professional Interactive Chart (Candlestick + Volume)
    st.subheader(f"MARKET ACTION: {selected_ticker}")
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=(f'{selected_ticker} Price (USD)', 'Volume'), 
                        row_width=[0.2, 0.7])

    # Candlestick
    fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
    # Moving Averages
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_20'], line=dict(color='orange', width=1.5), name='20-Day SMA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], line=dict(color='blue', width=1.5), name='50-Day SMA'), row=1, col=1)
    # Volume subplot
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name='Volume', marker_color='rgba(128, 128, 128, 0.5)'), row=2, col=1)
    
    fig.update_layout(xaxis_rangeslider_visible=False, template='plotly_dark', height=600, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # 5. Financial Metrics & Earnings Section
    st.subheader("FINANCIAL METRICS & EARNINGS SURPRISE")
    
    with st.spinner("Fetching institutional data..."):
        ticker_data = yf.Ticker(selected_ticker)
        col1, col2, col3 = st.columns(3)
        
        # Col 1: Analyst Consensus
        with col1:
            st.markdown("**Analyst Consensus & Price Targets**")
            try:
                info = ticker_data.info
                rec = info.get('recommendationKey', 'N/A').upper()
                mean_target = info.get('targetMeanPrice', 'N/A')
                high_target = info.get('targetHighPrice', 'N/A')
                low_target = info.get('targetLowPrice', 'N/A')
                
                st.write(f"- **Recommendation:** {rec}")
                st.write(f"- **Mean Target:** ${mean_target}")
                st.write(f"- **High Target:** ${high_target}")
                st.write(f"- **Low Target:** ${low_target}")
            except Exception:
                st.info("Analyst targets currently unavailable.")
        
        # Col 2: Earnings History (Cleaned up the "None" outputs)
        with col2:
            st.markdown("**Upcoming & Recent Earnings**")
            try:
                earnings_dates = ticker_data.get_earnings_dates(limit=4)
                if earnings_dates is not None and not earnings_dates.empty:
                    earnings_dates.index = earnings_dates.index.tz_localize(None)
                    
                    # Convert to string and replace messy API outputs with 'Pending'
                    disp_df = earnings_dates[['EPS Estimate', 'Reported EPS', 'Surprise(%)']].copy()
                    disp_df = disp_df.astype(str)
                    disp_df = disp_df.replace({'nan': 'Pending', 'None': 'Pending', '<NA>': 'Pending'})
                    
                    st.dataframe(disp_df)
                else:
                    st.info("No recent earnings surprise data available.")
            except Exception:
                st.info("Earnings calendar currently unavailable.")
        
        # Col 3: Key Financials (Top-line in Billions)
        with col3:
            st.markdown("**Income Statement (Top-Line)**")
            try:
                income = ticker_data.income_stmt
                if income is not None and not income.empty:
                    # Select specific rows if available to match institutional standards
                    target_rows = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income']
                    available_rows = [row for row in target_rows if row in income.index]
                    
                    if available_rows:
                        top_line = income.loc[available_rows].iloc[:, :2] # Get last 2 periods
                    else:
                        top_line = income.head(4).iloc[:, :2]
                        
                    # Format as Billions for readability
                    top_line = top_line.applymap(lambda x: f"${x/1000000000:,.2f}B" if pd.notnull(x) else "N/A")
                    st.dataframe(top_line)
                else:
                    st.info("Income statement data currently unavailable.")
            except Exception:
                st.info("Financial statements are temporarily rate-limited.")
                
    st.divider()

    # 6. Recent News Feed
    st.subheader("RECENT CATALYSTS & NEWS FEED")
    try:
        news = ticker_data.news
        if news and len(news) > 0:
            # Display the top 3 most recent news headlines
            for item in news[:3]:
                title = item.get('title', 'No title')
                publisher = item.get('publisher', 'Unknown source')
                link = item.get('link', '#')
                st.markdown(f"- **[{title}]({link})** ({publisher})")
        else:
            st.write("No recent news available.")
    except Exception:
        st.info("News feed currently unavailable.")

    st.divider()

    # 7. Local AI Analyst Summary
    st.subheader("AI QUANTITATIVE BRIEFING")
    if st.button(f"Generate Briefing for {selected_ticker}"):
        with st.spinner("Running local quantitative inference..."):
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

            try:
                response = ollama.chat(model='llama3', messages=[
                    {"role": "system", "content": "You are a Wall Street Equity Research Analyst."},
                    {"role": "user", "content": prompt}
                ])
                
                if isinstance(response, dict):
                    st.write(response['message']['content'])
                else:
                    st.write(response.message.content)
            except Exception as e:
                st.error(f"Inference failed. Error: {e}")

except FileNotFoundError:
    st.error(f"No local data found for {selected_ticker}. Run 'python src/fetch_market_data.py' to update your local store.")
