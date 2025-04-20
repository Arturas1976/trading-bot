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

SYMBOLS = ["EURUSD", "GBPUSD", "AAPL", "TSLA"]

def send_telegram_message(message: str):
    for chat_id in CHAT_IDS:
        if chat_id:
            try:
                requests.post(TELEGRAM_URL, data={"chat_id": chat_id, "text": message})
            except requests.RequestException as e:
                print(f"Telegram error: {e}")

def fetch_data(symbol: str, interval="15min", outputsize="compact"):
    function = "TIME_SERIES_INTRADAY"
    if symbol.endswith("USD"):
        function = "FX_INTRADAY"
        from_symbol = symbol[:3]
        to_symbol = symbol[3:]
        url = f"https://www.alphavantage.co/query?function={function}&from_symbol={from_symbol}&to_symbol={to_symbol}&interval={interval}&outputsize={outputsize}&apikey={ALPHA_VANTAGE_API_KEY}"
    else:
        url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={ALPHA_VANTAGE_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        time_series_key = f"Time Series ({interval})"
        if time_series_key not in data:
            raise ValueError(f"No data for {symbol}")
        df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        })
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        print(f"Data fetch error for {symbol}: {e}")
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
