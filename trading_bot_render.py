import os
import requests
import pandas as pd
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS = [os.getenv("CHAT_ID_1"), os.getenv("CHAT_ID_2")]
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

SYMBOLS = []

forex_pairs = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"
]

crypto_pairs = [
    "DOTUSD", "ATOMUSD", "ICPUSD", "SANDUSD", "MANTAUSD", "SOLUSD", 
    "ETHUSD", "DOGEUSD", "BTCUSD", "LINKUSD", "AVAXUSD", "ADAUSD", "MATICUSD"
]

stock_symbols = [
    "AAPL", "TSLA", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "NFLX", "JPM", "V"
]

SYMBOLS = forex_pairs + crypto_pairs + stock_symbols

def send_telegram_message(message: str):
    for chat_id in CHAT_IDS:
        if chat_id:
            try:
                requests.post(TELEGRAM_URL, data={"chat_id": chat_id, "text": message})
            except requests.RequestException as e:
                print(f"Telegram error: {e}")

def fetch_data(symbol):
    try:
        if symbol.endswith("USD") and symbol not in ["AAPL", "TSLA", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "NFLX", "JPM", "V"]:
            # Anta att det är en kryptovaluta
            function = "CRYPTO_INTRADAY"
            market = "USD"
            url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol[:-3]}&market={market}&interval=15min&apikey={API_KEY}&outputsize=compact"
            response = requests.get(url)
            data = response.json().get("Time Series Crypto (15min)", {})
        elif symbol in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"]:
            # Forex-par
            function = "FX_INTRADAY"
            url = f"https://www.alphavantage.co/query?function={function}&from_symbol={symbol[:3]}&to_symbol={symbol[3:]}&interval=15min&apikey={API_KEY}&outputsize=compact"
            response = requests.get(url)
            data = response.json().get("Time Series FX (15min)", {})
        else:
            # Anta att det är en aktie
            function = "TIME_SERIES_INTRADAY"
            url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval=15min&apikey={API_KEY}&outputsize=compact"
            response = requests.get(url)
            data = response.json().get("Time Series (15min)", {})

        if not data:
            raise Exception(f"{symbol}: No valid time series data found.")

        df = pd.DataFrame.from_dict(data, orient='index')
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        return df

    except Exception as e:
        print(f"Failed to fetch data for {symbol}: {e}")
        return None

def generate_tp_sl(price: float, signal: str):
    if signal == "BUY":
        tp = price * 1.025
        sl = price * 0.985
    else:
        tp = price * 0.975
        sl = price * 1.015
    return round(tp, 5), round(sl, 5)

def check_signals(df: pd.DataFrame, symbol: str):
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    if latest["Close"] > previous["Close"]:
        signal_type = "BUY"
    elif latest["Close"] < previous["Close"]:
        signal_type = "SELL"
    else:
        return None
    tp, sl = generate_tp_sl(latest["Close"], signal_type)
    return {
        "symbol": symbol,
        "type": signal_type,
        "price": round(latest["Close"], 5),
        "take_profit": tp,
        "stop_loss": sl,
        "time": latest.name.strftime("%Y-%m-%d %H:%M")
    }

def analyze():
    for symbol in SYMBOLS:
        df = fetch_data(symbol)
        if df is None:
            continue
        signal = check_signals(df, symbol)
        if signal:
            message = (
                f"📊 {signal['symbol']} - {signal['type']} signal\n"
                f"🕒 {signal['time']}\n"
                f"💵 Pris: {signal['price']}\n"
                f"🎯 Take Profit: {signal['take_profit']}\n"
                f"🛑 Stop Loss: {signal['stop_loss']}"
            )
            send_telegram_message(message)

if __name__ == "__main__":
    send_telegram_message("🤖 Tradingbot är igång med 15-minutersintervall.")
    while True:
        analyze()
        time.sleep(900)  # 15 minuter
