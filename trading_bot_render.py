import yfinance as yf
import pandas as pd
import telegram
from telegram import Bot
from telegram.error import TelegramError
import time
import logging
from datetime import datetime

# Lägg till dina Telegram-användar-ID:n i .env
TELEGRAM_TOKEN = 'your_telegram_bot_token_here'
TELEGRAM_USERS = ['user_id_1', 'user_id_2']

# Inställningar för analys
TIME_INTERVAL = '15m'

# Skapa en Bot-objekt
bot = Bot(token=TELEGRAM_TOKEN)

# Skapa loggning
logging.basicConfig(level=logging.INFO)

# Skicka ett meddelande till alla Telegram-användare
def send_telegram_message(message):
    for user_id in TELEGRAM_USERS:
        try:
            bot.send_message(chat_id=user_id, text=message)
        except TelegramError as e:
            logging.error(f"Error sending message to {user_id}: {e}")

# Hämta prisdata och utför analys
def get_stock_data(symbol):
    try:
        data = yf.download(symbol, period="1d", interval=TIME_INTERVAL)
        if data.empty:
            raise ValueError(f"No data found for {symbol}")
        return data
    except Exception as e:
        send_telegram_message(f"Fel med {symbol}: {str(e)}")
        return None

# RSI beräkning
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# MACD beräkning
def calculate_macd(data):
    macd_line = data['Close'].ewm(span=12, adjust=False).mean() - data['Close'].ewm(span=26, adjust=False).mean()
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal_line

# Analysera signaler
def analyze_signal(symbol, data):
    if data is None:
        return
    
    # Beräkna RSI och MACD
    rsi = calculate_rsi(data)
    macd_line, signal_line = calculate_macd(data)

    latest_rsi = rsi.iloc[-1]
    latest_macd = macd_line.iloc[-1]
    latest_signal = signal_line.iloc[-1]

    # RSI och MACD analys
    if latest_rsi < 30 and latest_macd > latest_signal:
        send_telegram_message(f"KÖP-signal för {symbol} - RSI: {latest_rsi:.2f}, MACD: {latest_macd:.2f}, Signal: {latest_signal:.2f}")
    elif latest_rsi > 70 and latest_macd < latest_signal:
        send_telegram_message(f"SÄLJ-signal för {symbol} - RSI: {latest_rsi:.2f}, MACD: {latest_macd:.2f}, Signal: {latest_signal:.2f}")
    else:
        send_telegram_message(f"Ingen signal för {symbol} - RSI: {latest_rsi:.2f}, MACD: {latest_macd:.2f}, Signal: {latest_signal:.2f}")

# Kör boten och analysera varje aktie/valuta/krypto
def run_bot():
    symbols = [
        'AAPL', 'TSLA', 'GOOG', 'AMZN', 'BTC-USD', 'ETH-USD', 'MATIC-USD=X', 'DOGE-USD', 'EURUSD=X', 'GBPUSD=X'
    ]
    
    send_telegram_message("Boten är nu igång!")
    
    while True:
        for symbol in symbols:
            data = get_stock_data(symbol)
            analyze_signal(symbol, data)
        
        time.sleep(900)  # Vänta 15 minuter innan nästa körning

if __name__ == "__main__":
    try:
        run_bot()
    except Exception as e:
        send_telegram_message(f"Ett fel har inträffat: {str(e)}")
        logging.error(f"Bot stopped due to error: {str(e)}")
