import os
import time
import requests
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime

# Telegram Bot Token och Chat ID från miljövariabler
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id_1 = os.getenv('CHAT_ID_1')
chat_id_2 = os.getenv('CHAT_ID_2')

# Funktion för att skicka meddelanden till Telegram
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.get(url, params=params)
    return response.json()

# Beräkna Stop Loss och Take Profit
def calculate_take_profit_and_stop_loss(entry_price, volatility=0.02):
    # Stop Loss och Take Profit baserat på 2% volatilitet (kan justeras)
    stop_loss = entry_price * (1 - volatility)  # 2% under köppriset
    take_profit = entry_price * (1 + volatility)  # 2% över köppriset
    return stop_loss, take_profit

# Funktion för att hämta marknadsdata
def fetch_data(symbol, interval='15m', period='1d'):
    data = yf.download(symbol, interval=interval, period=period)
    return data

# Funktion för att beräkna RSI
def calculate_rsi(data):
    rsi = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
    return rsi

# Funktion för att beräkna MACD
def calculate_macd(data):
    macd = ta.trend.MACD(data['Close'])
    macd_signal = macd.macd_signal()
    macd_diff = macd.macd_diff()
    return macd, macd_signal, macd_diff

# Huvudfunktion som kontrollerar signalerna och skickar ut dem
def check_and_send_signal(symbol):
    data = fetch_data(symbol)
    rsi = calculate_rsi(data)
    macd, macd_signal, macd_diff = calculate_macd(data)

    # Senaste RSI och MACD-värden
    latest_rsi = rsi.iloc[-1]
    latest_macd = macd.iloc[-1]
    latest_macd_signal = macd_signal.iloc[-1]
    latest_macd_diff = macd_diff.iloc[-1]

    entry_price = data['Close'].iloc[-1]  # Senaste stängningspriset

    # Logik för köp och sälj baserat på RSI och MACD
    if latest_rsi <= 30 and latest_macd_diff > 0:  # RSI under 30 och MACD positivt – köp
        stop_loss, take_profit = calculate_take_profit_and_stop_loss(entry_price)
        message = f"Köp Signal för {symbol}:\n" \
                  f"Köppris: {entry_price}\n" \
                  f"RSI: {latest_rsi}\n" \
                  f"MACD: {latest_macd}\n" \
                  f"Rekommenderad Stop Loss: {stop_loss:.2f}\n" \
                  f"Rekommenderad Take Profit: {take_profit:.2f}"
        send_message(chat_id_1, message)
        send_message(chat_id_2, message)

    elif latest_rsi >= 70 and latest_macd_diff < 0:  # RSI över 70 och MACD negativt – sälj
        stop_loss, take_profit = calculate_take_profit_and_stop_loss(entry_price)
        message = f"Sälj Signal för {symbol}:\n" \
                  f"Säljpris: {entry_price}\n" \
                  f"RSI: {latest_rsi}\n" \
                  f"MACD: {latest_macd}\n" \
                  f"Rekommenderad Stop Loss: {stop_loss:.2f}\n" \
                  f"Rekommenderad Take Profit: {take_profit:.2f}"
        send_message(chat_id_1, message)
        send_message(chat_id_2, message)

# Testsignal vid start
def test_signal():
    message = "Testsignal: Boten är igång och fungerar korrekt!"
    send_message(chat_id_1, message)
    send_message(chat_id_2, message)

# Testa med ett valfritt symbol
test_signal()

# Huvudloop som kollar signaler var 15:e minut
while True:
    check_and_send_signal('BTC-USD')  # Byt ut med symbolen du vill övervaka
    check_and_send_signal('ETH-USD')  # Lägg till fler symboler här
    check_and_send_signal('XAUUSD=X')  # Guld mot USD (kan också bytas ut)
    time.sleep(900)  # Vänta i 15 minuter (900 sekunder)
