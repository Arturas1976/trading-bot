import os
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "").split(",")

bot = Bot(token=TELEGRAM_TOKEN)

# === SYMBOLER ===
forex_pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"]
crypto_pairs = ["DOTUSD", "ATOMUSD", "ICPUSD", "SANDUSD", "MANTAUSD", "SOLUSD", "ETHUSD", "DOGEUSD", "BTCUSD", "LINKUSD", "AVAXUSD", "ADAUSD", "MATICUSD"]
stock_symbols = ["AAPL", "TSLA", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "NFLX", "JPM", "V"]

SYMBOLS = forex_pairs + crypto_pairs + stock_symbols

def fetch_data(symbol):
    try:
        if symbol.endswith("USD") and symbol not in stock_symbols:
            url = f"https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol={symbol[:-3]}&market=USD&interval=15min&apikey={API_KEY}&outputsize=compact"
            data = requests.get(url).json().get("Time Series Crypto (15min)", {})
        elif symbol in forex_pairs:
            url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={symbol[:3]}&to_symbol={symbol[3:]}&interval=15min&apikey={API_KEY}&outputsize=compact"
            data = requests.get(url).json().get("Time Series FX (15min)", {})
        else:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=15min&apikey={API_KEY}&outputsize=compact"
            data = requests.get(url).json().get("Time Series (15min)", {})

        if not data:
            raise Exception(f"{symbol}: No valid time series data found.")
        df = pd.DataFrame.from_dict(data, orient='index').astype(float)
        df.index = pd.to_datetime(df.index)
        return df.sort_index()
    except Exception as e:
        print(f"Failed to fetch data for {symbol}: {e}")
        return None

def generate_signals(df):
    df["SMA_20"] = df["4. close"].rolling(window=20).mean()
    df["SMA_50"] = df["4. close"].rolling(window=50).mean()
    signal = None
    if df["SMA_20"].iloc[-2] < df["SMA_50"].iloc[-2] and df["SMA_20"].iloc[-1] > df["SMA_50"].iloc[-1]:
        signal = "BUY"
    elif df["SMA_20"].iloc[-2] > df["SMA_50"].iloc[-2] and df["SMA_20"].iloc[-1] < df["SMA_50"].iloc[-1]:
        signal = "SELL"
    return signal

def calculate_tp_sl(price, signal):
    tp = sl = None
    if signal == "BUY":
        tp = price * 1.02
        sl = price * 0.98
    elif signal == "SELL":
        tp = price * 0.98
        sl = price * 1.02
    return round(tp, 2), round(sl, 2)

def send_telegram_message(message):
    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            bot.send_message(chat_id=chat_id.strip(), text=message)
        except Exception as e:
            print(f"Telegram error: {e}")

def run_bot():
    print(f"Running bot... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for symbol in SYMBOLS:
        df = fetch_data(symbol)
        if df is not None and len(df) >= 50:
            signal = generate_signals(df)
            if signal:
                price = df["4. close"].iloc[-1]
                tp, sl = calculate_tp_sl(price, signal)
                message = (
                    f"📈 Signal: {signal}\n"
                    f"💹 Symbol: {symbol}\n"
                    f"📊 Price: {price:.2f}\n"
                    f"🎯 TP: {tp}\n"
                    f"🛑 SL: {sl}\n"
                    f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                send_telegram_message(message)
    print("Cycle complete.\n")

if __name__ == "__main__":
    while True:
        run_bot()
        time.sleep(900)  # 15 min
