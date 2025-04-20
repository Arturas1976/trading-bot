import yfinance as yf
from telegram import Bot
import pandas as pd
from dotenv import load_dotenv
import os
import time
import traceback

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USERS = os.getenv("TELEGRAM_USERS", "").split(",")

bot = Bot(token=TELEGRAM_TOKEN)
sent_errors = set()

symbols = [
    # Forex
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X",

    # Stocks
    "AAPL", "MSFT", "GOOG", "TSLA", "AMZN", "NVDA", "META", "NFLX", "JPM", "V",

    # Crypto (USD-paret)
    "ETH-USD", "BTC-USD", "SOL-USD", "DOGE-USD", "DOT-USD", "ATOM-USD",
    "ICP-USD", "SAND-USD", "MANTA-USD", "AVAX-USD", "LINK-USD", "NEAR-USD"
]

def get_rsi(data, period: int = 14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_macd(data):
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def analyze(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="15m")
        if df.empty:
            raise Exception(f"{symbol}: No price data found")

        df['RSI'] = get_rsi(df)
        df['MACD'], df['MACD_signal'] = get_macd(df)

        rsi = df['RSI'].iloc[-1]
        macd = df['MACD'].iloc[-1]
        macd_signal = df['MACD_signal'].iloc[-1]

        signal = None
        tp = None
        sl = None

        if rsi < 30 and macd > macd_signal:
            signal = "KÖP"
            tp = round(df['Close'].iloc[-1] * 1.02, 2)
            sl = round(df['Close'].iloc[-1] * 0.98, 2)
        elif rsi > 70 and macd < macd_signal:
            signal = "SÄLJ"
            tp = round(df['Close'].iloc[-1] * 0.98, 2)
            sl = round(df['Close'].iloc[-1] * 1.02, 2)

        if signal:
            price = df['Close'].iloc[-1]
            message = (
                f"📊 *{symbol}*\n"
                f"Signal: *{signal}*\n"
                f"Pris: ${price:.2f}\n"
                f"TP: ${tp}\n"
                f"SL: ${sl}\n"
                f"RSI: {rsi:.2f}\n"
                f"MACD: {macd:.2f}, Signal: {macd_signal:.2f}"
            )
            for chat_id in TELEGRAM_USERS:
                bot.send_message(chat_id=chat_id.strip(), text=message, parse_mode="Markdown")

    except Exception as e:
        if symbol not in sent_errors:
            error_message = f"⚠️ Fel med {symbol}: {str(e)}"
            for chat_id in TELEGRAM_USERS:
                bot.send_message(chat_id=chat_id.strip(), text=error_message)
            sent_errors.add(symbol)

def main():
    for chat_id in TELEGRAM_USERS:
        bot.send_message(chat_id=chat_id.strip(), text="🤖 Tradingboten är igång!")

    while True:
        for symbol in symbols:
            analyze(symbol)
        time.sleep(15 * 60)

if __name__ == "__main__":
    main()
