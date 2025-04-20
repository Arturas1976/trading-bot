import os
import requests
import time
import talib
import numpy as np
import yfinance as yf
from telegram import Bot

# Hämtar miljövariabler från Render
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Din Telegram Bot Token
group_chat_id = os.getenv('GROUP_CHAT_ID')  # Din Telegram gruppens Chat ID

# Initiera Telegram Bot
bot = Bot(token=API_TOKEN)

# Skicka ett testmeddelande till Telegram-gruppen vid uppstart
def send_test_message():
    try:
        bot.send_message(chat_id=group_chat_id, text="Signalai aktyvus!")
    except Exception as e:
        print(f"Fel vid testmeddelande: {e}")

# Funktion för att skicka meddelanden till Telegram
def send_to_telegram(message):
    try:
        bot.send_message(chat_id=group_chat_id, text=message)
    except Exception as e:
        print(f"Fel vid skickande till gruppen: {e}")

# Funktion för att analysera aktier/valutor och ge signaler
def analyze_stock(symbol):
    # Hämta historisk data från Yahoo Finance
    data = yf.download(symbol, period="5d", interval="15m")
    
    # Beräkna tekniska indikatorer
    rsi = talib.RSI(data['Close'], timeperiod=14)[-1]  # RSI
    macd, macdsignal, macdhist = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    upperband, middleband, lowerband = talib.BBANDS(data['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

    # Skapa meddelande baserat på indikatorvärden
    message = f"Analyserar {symbol}:\n"
    
    # RSI Signal
    if rsi < 30:
        message += f"RSI är under 30 – *Köp signal*\n"
    elif rsi > 70:
        message += f"RSI är över 70 – *Sälj signal*\n"

    # MACD Signal
    if macd[-1] > macdsignal[-1]:
        message += "MACD signal: Köp\n"
    elif macd[-1] < macdsignal[-1]:
        message += "MACD signal: Sälj\n"

    # Bollinger Bands Signal
    if data['Close'][-1] < lowerband[-1]:
        message += "Bollinger Bands: Köp\n"
    elif data['Close'][-1] > upperband[-1]:
        message += "Bollinger Bands: Sälj\n"

    # Skicka sammanfattning till Telegram
    send_to_telegram(message)
    return message

# Funktion för att köra boten och analysera olika symboler
def main():
    # Symboler att övervaka
    symbols = ['BTC-USD', 'ETH-USD', 'AAPL', 'GOOG', 'EURUSD=X']

    # Skicka testmeddelande vid uppstart
    send_test_message()

    # Huvudloop för att kontinuerligt analysera och skicka signaler var 15:e minut
    while True:
        for symbol in symbols:
            message = analyze_stock(symbol)
            print(f"Skickade meddelande för {symbol}: {message}")
        time.sleep(60 * 15)  # Vänta 15 minuter innan nästa analys

if __name__ == "__main__":
    main()
