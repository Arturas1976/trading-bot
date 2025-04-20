import os
import time
import requests
import yfinance as yf
import talib as ta
from datetime import datetime

# Telegram Bot token och chat id
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Din Telegram Bot Token
chat_id_1 = os.getenv('CHAT_ID_1')  # Första Telegram Chat ID
chat_id_2 = os.getenv('CHAT_ID_2')  # Andra Telegram Chat ID

# Funktion för att skicka meddelande till Telegram
def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    response = requests.get(url)
    return response.json()

# Funktion för att hämta RSI och skapa signaler
def get_rsi_signal():
    # Hämta senaste data för BTC/USD
    symbol = 'BTC-USD'
    data = yf.download(symbol, period="1d", interval="15m")
    
    # Beräkna RSI
    close_prices = data['Close']
    rsi = ta.RSI(close_prices, timeperiod=14)[-1]  # Få senaste RSI-värdet

    # Skapa signal baserat på RSI
    if rsi < 30:
        return "RSI är under 30 - *KÖP*"
    elif rsi > 70:
        return "RSI är över 70 - *SÄLJ*"
    else:
        return "RSI är neutral - *HÅLL*"

# Skicka testsignal vid scriptstart
def send_test_signal():
    message = "Testsignal: Bot är igång och redo att skicka signals!"
    send_message(chat_id_1, message)
    send_message(chat_id_2, message)

# Huvudlogik för att köra signaler
def main():
    send_test_signal()  # Skicka en testsignal vid start
    while True:
        signal = get_rsi_signal()  # Hämta signal
        print(f"{datetime.now()}: {signal}")  # Skriv ut signal i terminalen
        send_message(chat_id_1, signal)  # Skicka till första Telegram chat
        send_message(chat_id_2, signal)  # Skicka till andra Telegram chat
        time.sleep(900)  # Vänta 15 minuter (900 sekunder) innan nästa signal

if __name__ == "__main__":
    main()
