import os
import pandas as pd
import ollama
from datetime import datetime

def analyze_stock_trend(ticker):
    print(f"Analyzing {ticker} data...")
    
    # 1. Read the latest data (Make sure the date matches today's date in your filename!)
    today_str = datetime.now().strftime('%Y%m%d')
    file_path = f"data/raw/{ticker}_raw_{today_str}.csv"
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Could not find data for {ticker}. Did you run fetch_market_data.py today?")
        return

    # 2. Process the data (Extract the last 5 days of closing prices)
    recent_data = df.tail(5)
    trend_text = recent_data.to_string(index=False)
    
    # 3. Prompt the Local AI Agent with the Wall Street Persona
    print("Generating Wall Street AI market summary using Llama 3...")
    prompt = f"""
    You are a Senior Equity Research Analyst at a top-tier Wall Street investment bank. 
    Review the following 5-day trailing closing prices for {ticker}:
    {trend_text}
    
    Provide a concise, 2-sentence market update suitable for an institutional morning briefing. 
    Focus on price action, momentum, and technical sentiment. 
    Use professional financial terminology (e.g., 'consolidating', 'bullish/bearish divergence', 'testing support/resistance', 'price discovery') where appropriate. 
    Maintain an objective, highly professional, and analytical tone.
    """

    try:
        # Using the local Ollama client to run the open-source model
        response = ollama.chat(model='llama3', messages=[
            {"role": "system", "content": "You are a Wall Street Equity Research Analyst."},
            {"role": "user", "content": prompt}
        ])
        
        # 4. Output the result
        print("\n--- LOCAL AI MARKET SUMMARY ---")
        
        # The ollama library might return a dictionary or an object depending on version, 
        # so we extract the content safely.
        if isinstance(response, dict):
            print(response['message']['content'])
        else:
            print(response.message.content)
            
        print("-------------------------------\n")
        
    except Exception as e:
        print(f"Failed to connect to local AI. Is Ollama installed and running? Error: {e}")

if __name__ == "__main__":
    analyze_stock_trend("MSFT")
