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
        if df.empty or len(df) < 30:
            raise Exception(f"{symbol}: Otillräcklig data för analys")

        df['RSI'] = get_rsi(df)
        df['MACD'], df['MACD_signal'] = get_macd(df)

        latest_data = df.iloc[-1]
        rsi = latest_data['RSI']
        macd = latest_data['MACD']
        macd_signal = latest_data['MACD_signal']
        close_price = latest_data['Close']

        signal = None
        tp = None
        sl = None

        if rsi < 30 and macd > macd_signal:
            signal = "KÖP"
            tp = round(close_price * 1.02, 2)
            sl = round(close_price * 0.98, 2)
        elif rsi > 70 and macd < macd_signal:
            signal = "SÄLJ"
            tp = round(close_price * 0.98, 2)
            sl = round(close_price * 1.02, 2)

        if signal:
            message = (
                f"📊 *{symbol}*\n"
                f"Signal: *{signal}*\n"
                f"Pris: ${close_price:.2f}\n"
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