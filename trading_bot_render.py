import yfinance as yf
import pandas as pd
import ta
import time
import os
import requests
import logging
from datetime import datetime

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
chat_ids = [
    os.getenv('CHAT_ID_1'),
    os.getenv('CHAT_ID_2'),
]

SYMBOLS = ['BTC-USD', 'ETH-USD', 'AAPL', 'SOL-USD', 'EURUSD=X', 'TSLA', 'XAUUSD=X']
INTERVAL = '15m'
LOOKBACK_PERIOD = '1d'

sent_signals = {}

logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
)

def send_telegram_message(message):
    for chat_id in chat_ids:
        try:
            url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
            data = {"chat_id": chat_id, "text": message}
            requests.post(url, data=data)
        except Exception as e:
            logging.error(f"Telegram error: {e}")

def fetch_data(symbol):
    try:
        df = yf.download(symbol, interval=INTERVAL, period=LOOKBACK_PERIOD)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        logging.error(f"Klaida paimant duomenis {symbol}: {e}")
        return None

def analyze(symbol):
    df = fetch_data(symbol)
    if df is None or len(df) < 50:
        return

    try:
        df['rsi'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        macd = ta.trend.MACD(df['Close'])
        df['macd_diff'] = macd.macd_diff()
        bb = ta.volatility.BollingerBands(df['Close'])
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        last = df.iloc[-1]
        prev = df.iloc[-2]

        signal = None

        if prev['rsi'] > 30 and last['rsi'] <= 30:
            if last['macd_diff'] > 0 and last['Close'] < last['bb_lower']:
                signal = f"📈 PIRKTI {symbol} (RSI kerta žemyn 30, MACD teigiamas, žemiau Bollinger)"
        elif prev['rsi'] < 70 and last['rsi'] >= 70:
            if last['macd_diff'] < 0 and last['Close'] > last['bb_upper']:
                signal = f"📉 PARDUOTI {symbol} (RSI kerta aukštyn 70, MACD neigiamas, aukščiau Bollinger)"

        if signal:
            if sent_signals.get(symbol) != signal:
                send_telegram_message(signal)
                sent_signals[symbol] = signal
                logging.info(signal)
    except Exception as e:
        logging.error(f"Klaida analizuojant {symbol}: {e}")

def send_test_signal():
    send_telegram_message("✅ Test signalas: botas paleistas sėkmingai!")
    logging.info("Test signalas išsiųstas.")

def summary():
    text = "📊 Dienos suvestinė:\n"
    for symbol, signal in sent_signals.items():
        text += f"{symbol}: {signal}\n"
    send_telegram_message(text)

send_test_signal()

while True:
    for symbol in SYMBOLS:
        analyze(symbol)
    time.sleep(900)  # 15 minučių
