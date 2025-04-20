import time
import yfinance as yf
import ta
import requests
import os

# Hämtar Telegram API Token och Chat ID via miljövariabler
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Din Telegram Bot Token
chat_id_1 = os.getenv('CHAT_ID_1')  # Första Telegram Chat ID
chat_id_2 = os.getenv('CHAT_ID_2')  # Andra Telegram Chat ID

# Funktion för att skicka meddelande till Telegram
def send_message_to_telegram(message):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    
    # Skicka till båda chat-id:n
    params_1 = {
        "chat_id": chat_id_1,
        "text": message
    }
    params_2 = {
        "chat_id": chat_id_2,
        "text": message
    }
    
    try:
        # Skicka till första chat-id
        response_1 = requests.get(url, params=params_1)
        if response_1.status_code != 200:
            print(f"Failed to send message to chat_id_1: {response_1.status_code}, {response_1.text}")
        
        # Skicka till andra chat-id
        response_2 = requests.get(url, params=params_2)
        if response_2.status_code != 200:
            print(f"Failed to send message to chat_id_2: {response_2.status_code}, {response_2.text}")
    
    except Exception as e:
        print(f"Error sending message: {e}")

# Testsignal när boten startar, skickas endast en gång
def send_initial_message():
    send_message_to_telegram("Botten är online och fungerar!")

# Funktion för att hämta marknadsdata och beräkna tekniska indikatorer
def fetch_data():
    try:
        # Här hämtar vi marknadsdata för Bitcoin som exempel, ändra symbolen för andra instrument
        data = yf.download('BTC-USD', period='1d', interval='15m')

        # Kontrollera att vi har data
        if data.empty:
            print("Ingen data mottogs.")
            return None
        
        # Beräkna RSI med hjälp av ta-biblioteket
        rsi_indicator = ta.momentum.RSIIndicator(data['Close'], window=14)
        data['rsi'] = rsi_indicator.rsi()

        # Lägg till fler tekniska indikatorer vid behov
        # T.ex., MA, MACD, Bollinger Bands osv.

        return data
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Funktion för att skicka köp-/säljsignaler baserat på RSI
def check_signals(data):
    if data is None:
        return

    latest_rsi = data['rsi'].iloc[-1]  # Senaste RSI-värdet

    # När RSI är under 30, köp
    if latest_rsi < 30:
        send_message_to_telegram("RSI är under 30 - KÖP!")

    # När RSI är över 70, sälj
    elif latest_rsi > 70:
        send_message_to_telegram("RSI är över 70 - SÄLJ!")

# Skicka testmeddelande vid uppstart
if __name__ == "__main__":
    # Skicka endast ett meddelande vid start
    send_initial_message()

    # Huvudloop för att hämta data och kontrollera signaler
    while True:
        data = fetch_data()
        if data is not None:
            check_signals(data)
        
        # Vänta 15 minuter innan nästa kontroll (inte varje minut)
        time.sleep(15 * 60)
