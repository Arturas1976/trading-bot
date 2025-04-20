import os
import time
import yfinance as yf
import pandas as pd
import ta
import requests
from datetime import datetime

# Din Telegram Bot Token och Chat IDs
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Din Telegram Bot Token
chat_id_1 = os.getenv('CHAT_ID_1')  # Första Telegram Chat ID
chat_id_2 = os.getenv('CHAT_ID_2')  # Andra Telegram Chat ID

# Funktion för att hämta data
def fetch_data(symbol, period='1d', interval='1m'):
    data = yf.download(symbol, period=period, interval=interval)
    data['rsi'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
    data['macd'] = ta.trend.MACD(data['Close']).macd()
    return data

# Skicka signaler till Telegram
def send_signal(message, chat_id):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    requests.post(url, data=payload)

# Kontrollera RSI och MACD och ge signaler
def check_signal(data, symbol):
    last_rsi = data['rsi'].iloc[-1]
    last_macd = data['macd'].iloc[-1]
    message = ""
    
    # Köpsignal: RSI under 30 och MACD positiv
    if last_rsi < 30 and last_macd > 0:
        message = f"KÖP signal för {symbol}! RSI: {last_rsi}, MACD: {last_macd}. Rekommendation: Stop Loss vid {data['Close'].iloc[-1] * 0.98}, Take Profit vid {data['Close'].iloc[-1] * 1.05}."
        
    # Säljsignal: RSI över 70 och MACD negativ
    elif last_rsi > 70 and last_macd < 0:
        message = f"SÄLJ signal för {symbol}! RSI: {last_rsi}, MACD: {last_macd}. Rekommendation: Stop Loss vid {data['Close'].iloc[-1] * 1.02}, Take Profit vid {data['Close'].iloc[-1] * 0.95}."
        
    return message

# Skicka testmeddelande till båda konton vid start
def send_test_signal():
    message = "Test Signal: Boten är igång och redo att ge signaler!"
    send_signal(message, chat_id_1)
    send_signal(message, chat_id_2)

# Huvudloop
def run_bot():
    symbols = ['BTC-USD', 'ETH-USD', 'XAUUSD=X', 'AAPL', 'TSLA', 'SOLANA-USD', 'EURUSD=X']  # Lägg till fler symboler här
    interval = 900  # 15 minuter i sekunder
    last_signal_time = 0  # Sista signal tid

    # Skicka testsignal en gång vid uppstart
    send_test_signal()

    while True:
        current_time = time.time()
        
        if current_time - last_signal_time >= interval:
            for symbol in symbols:
                data = fetch_data(symbol)
                signal = check_signal(data, symbol)
                
                if signal:
                    send_signal(signal, chat_id_1)  # Skicka signal till första chatten
                    send_signal(signal, chat_id_2)  # Skicka signal till andra chatten
                    last_signal_time = current_time  # Uppdatera senaste signal tid

        time.sleep(60)  # Vänta 1 minut innan nästa koll

if __name__ == "__main__":
    run_bot()
