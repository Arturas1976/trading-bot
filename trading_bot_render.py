import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
import time
import requests
import os

# Telegram settings
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id_1 = os.getenv('CHAT_ID_1')
chat_id_2 = os.getenv('CHAT_ID_2')

# Function to send messages to Telegram
def send_telegram_message(message, chat_id):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.get(url, params=params)
    return response.json()

# Fetch data for a symbol
def fetch_data(symbol):
    data = yf.download(symbol, period="1d", interval="15m")  # 15-minute interval data
    data = data[['Close']]  # Only use the 'Close' price
    data = data.reset_index()  # Reset index to handle any datetime issues
    data['Close'] = data['Close'].values  # Ensure 'Close' is a 1D array
    return data

# Calculate RSI
def calculate_rsi(data):
    rsi = RSIIndicator(data['Close'], window=14)  # RSI with a window size of 14
    return rsi.rsi()  # This returns a series which can be used directly

# Calculate MACD
def calculate_macd(data):
    macd = MACD(data['Close'], window_slow=26, window_fast=12, window_sign=9)  # MACD settings
    return macd.macd(), macd.macd_signal()  # Return MACD line and signal line

# Define trading symbols
symbols = ['BTC-USD', 'ETH-USD', 'AAPL', 'SOLANA', 'EURUSD=X', 'TESSLA', 'XAUUSD=X']  # Example symbols to analyze

# Main loop to analyze each symbol every 15 minutes
while True:
    for symbol in symbols:
        data = fetch_data(symbol)  # Fetch data for the symbol
        rsi = calculate_rsi(data)  # Calculate RSI
        macd, macd_signal = calculate_macd(data)  # Calculate MACD

        # Get the latest RSI and MACD values
        latest_rsi = rsi.iloc[-1]
        latest_macd = macd.iloc[-1]
        latest_macd_signal = macd_signal.iloc[-1]

        # Print the values for debugging
        print(f"{symbol}: RSI={latest_rsi}, MACD={latest_macd}, MACD Signal={latest_macd_signal}")

        # Check if RSI is below 30 and MACD is bullish (crossing above signal line) for buying signal
        if latest_rsi < 30 and latest_macd > latest_macd_signal:
            message = f"Buy Signal for {symbol}: RSI={latest_rsi}, MACD={latest_macd}, MACD Signal={latest_macd_signal}"
            send_telegram_message(message, chat_id_1)
            send_telegram_message(message, chat_id_2)

        # Check if RSI is above 70 and MACD is bearish (crossing below signal line) for selling signal
        elif latest_rsi > 70 and latest_macd < latest_macd_signal:
            message = f"Sell Signal for {symbol}: RSI={latest_rsi}, MACD={latest_macd}, MACD Signal={latest_macd_signal}"
            send_telegram_message(message, chat_id_1)
            send_telegram_message(message, chat_id_2)

    # Wait for 15 minutes before the next iteration
    time.sleep(900)  # 900 seconds = 15 minutes
