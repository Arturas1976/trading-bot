import os
import time
import requests
import yfinance as yf
import ta
import pandas as pd
from datetime import datetime

# Telegram Bot Setup
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id_1 = os.getenv('CHAT_ID_1')
chat_id_2 = os.getenv('CHAT_ID_2')

# List of symbols to analyze
symbols = [
    'BTC-USD', 'ETH-USD', 'GBPUSD=X', 'AUDUSD=X', 'USDJPY=X', 
    'TSLA', 'AAPL', 'GOOG', 'AMZN', 'MSFT', 'NVDA', 'META', 
    'SPY', 'NFLX', 'BCH-USD', 'SOL-USD', 'ADA-USD'
]

# Function to send message to Telegram
def send_telegram_message(message, chat_id):
    url = f'https://api.telegram.org/bot{API_TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': message}
    response = requests.post(url, data=data)
    return response.json()

# Function to calculate RSI and MACD
def calculate_indicators(data):
    rsi = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()[-1]
    macd = ta.trend.MACD(data['Close'], window_slow=26, window_fast=12, window_sign=9)
    macd_diff = macd.macd_diff()[-1]
    return rsi, macd_diff

# Function to fetch data from Yahoo Finance
def fetch_data(symbol):
    try:
        data = yf.download(symbol, period='1d', interval='15m')
        data.dropna(inplace=True)
        if data.empty:
            raise ValueError(f"No data found for {symbol}")
        return data
    except Exception as e:
        error_message = f"Error fetching data for {symbol}: {str(e)}"
        send_telegram_message(error_message, chat_id_1)
        send_telegram_message(error_message, chat_id_2)
        return None

# Function to get recommendation for take profit and stop loss
def get_recommendations(symbol, action, data):
    price = data['Close'].iloc[-1]
    tp = price * 1.05 if action == 'buy' else price * 0.95
    sl = price * 0.95 if action == 'buy' else price * 1.05
    return f"Recommendation: Take Profit at {tp:.2f}, Stop Loss at {sl:.2f}"

# Function to analyze the symbols
def analyze_symbols():
    for symbol in symbols:
        data = fetch_data(symbol)
        if data is None:
            continue  # Skip symbol if no data is available

        rsi, macd_diff = calculate_indicators(data)
        
        # Check if RSI and MACD conditions are met
        if rsi < 30 and macd_diff > 0:
            message = f"Buy Signal for {symbol}!\nRSI: {rsi:.2f}\nMACD Diff: {macd_diff:.2f}"
            recommendations = get_recommendations(symbol, 'buy', data)
            message += "\n" + recommendations
            send_telegram_message(message, chat_id_1)
            send_telegram_message(message, chat_id_2)

        elif rsi > 70 and macd_diff < 0:
            message = f"Sell Signal for {symbol}!\nRSI: {rsi:.2f}\nMACD Diff: {macd_diff:.2f}"
            recommendations = get_recommendations(symbol, 'sell', data)
            message += "\n" + recommendations
            send_telegram_message(message, chat_id_1)
            send_telegram_message(message, chat_id_2)

# Test signal on bot startup (only once)
def send_test_signal():
    message = "The Trading Bot is now live and running!"
    send_telegram_message(message, chat_id_1)
    send_telegram_message(message, chat_id_2)

# Signal if the bot doesn't work correctly
def send_error_signal(error_message):
    message = f"Alert: Something went wrong with the Trading Bot!\nError: {error_message}"
    send_telegram_message(message, chat_id_1)
    send_telegram_message(message, chat_id_2)

# Run the bot every 15 minutes
if __name__ == "__main__":
    send_test_signal()  # Send a test signal at the start (once)
    while True:
        try:
            analyze_symbols()
        except Exception as e:
            send_error_signal(str(e))
        time.sleep(900)  # 15 minutes interval
