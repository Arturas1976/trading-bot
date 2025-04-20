import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import time
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS = [os.getenv("CHAT_ID_1"), os.getenv("CHAT_ID_2")]
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# Forex + aktier
SYMBOLS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X",
    "AAPL", "MSFT", "TSLA", "GOOG", "AMZN", "NVDA", "META", "NFLX", "JPM", "V"
]

def send_telegram_message(message: str):
    for chat_id in CHAT_IDS:
        if chat_id:
            try:
                requests.post(TELEGRAM_URL, data={"chat_id": chat_id, "text": message})
            except requests.RequestException as e:
                print(f"Telegram error: {e}")

def fetch_data(symbol: str, interval="15m", period="1d"):
    try:
        df = yf.download(symbol, interval=interval, period=period)
        if df.empty:
            raise ValueError(f"No data for {symbol}")
        return df
    except Exception as e:
        print(f"Data fetch error for {symbol}: {e}")
        return None

def apply_indicators(df: pd.DataFrame):
    df = df.copy()
    df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    macd = ta.trend.MACD(df["Close"])
    df["macd_diff"] = macd.macd_diff()
    df["sma_20"] = ta.trend.SMAIndicator(df["Close"], window=20).sma_indicator()
    df["sma_50"] = ta.trend.SMAIndicator(df["Close"], window=50).sma_indicator()
    return df

def generate_tp_sl(price: float, signal: str):
    if signal == "BUY":
        tp = price * 1.025
        sl = price * 0.985
    else:  # SELL
        tp = price * 0.975
        sl = price * 1.015
    return round(tp, 2), round(sl, 2)

def check_signals(df: pd.DataFrame, symbol: str):
    latest = df.iloc[-1]
    signals = []

    if latest["rsi"] < 30 and latest["macd_diff"] > 0 and latest["sma_20"] > latest["sma_50"]:
        signal_type = "BUY"
    elif latest["rsi"] > 70 and latest["macd_diff"] < 0 and latest["sma_20"] < latest["sma_50"]:
        signal_type = "SELL"
    else:
        return None

    tp, sl = generate_tp_sl(latest["Close"], signal_type)
    return {
        "symbol": symbol,
        "type": signal_type,
        "price": round(latest["Close"], 2),
        "take_profit": tp,
        "stop_loss": sl,
        "time": latest.name.strftime("%Y-%m-%d %H:%M")
    }

def analyze():
    for symbol in SYMBOLS:
        df = fetch_data(symbol)
        if df is None:
            continue
        df = apply_indicators(df)
        signal = check_signals(df, symbol)

        if signal:
            message = (
                f"📊 *{signal['symbol']}* - {signal['type']} signal\n"
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
        time.sleep(900)  # Vänta 15 minuter
