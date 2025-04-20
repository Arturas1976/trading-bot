import yfinance as yf
import pandas as pd
import ta
import time
import os
from telegram import Bot

# Telegram inställningar från miljövariabler
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

# Symboler att övervaka
symbols = ["BTC-USD", "ETH-USD", "AAPL", "SOL-USD", "EURUSD=X", "TSLA", "GC=F"]  # Gold

# Funktion för att hämta marknadsdata
def fetch_data(symbol, interval="1h", period="7d"):
    df = yf.download(tickers=symbol, interval=interval, period=period)
    df.dropna(inplace=True)
    return df

# Lägg till tekniska indikatorer
def add_indicators(df):
    df['rsi'] = ta.momentum.RSIIndicator(close=df['Close']).rsi()
    df['ma'] = ta.trend.SMAIndicator(close=df['Close'], window=14).sma_indicator()
    macd = ta.trend.MACD(close=df['Close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    bb = ta.volatility.BollingerBands(close=df['Close'])
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    return df

# Skapa signal utifrån indikatorer
def generate_signal(df):
    last = df.iloc[-1]
    signal = []

    if last['rsi'] < 30:
        signal.append(f"🟢 RSI < 30 → KÖP ({last['rsi']:.2f})")
    elif last['rsi'] > 70:
        signal.append(f"🔴 RSI > 70 → SÄLJ ({last['rsi']:.2f})")

    if last['macd'] > last['macd_signal']:
        signal.append("📈 MACD signal → KÖP")
    elif last['macd'] < last['macd_signal']:
        signal.append("📉 MACD signal → SÄLJ")

    if last['Close'] < last['bb_lower']:
        signal.append("🧊 Under Bollinger Band → MÖJLIG BOTTEN")
    elif last['Close'] > last['bb_upper']:
        signal.append("🔥 Över Bollinger Band → MÖJLIG TOPP")

    return "\n".join(signal) if signal else None

# Skicka signal till Telegram
def send_to_telegram(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Fel vid sändning till Telegram: {e}")

# Huvudloop
def run_bot():
    while True:
        print("🔁 Kontrollerar marknaden...")
        for symbol in symbols:
            try:
                df = fetch_data(symbol)
                df = add_indicators(df)
                signal = generate_signal(df)
                if signal:
                    full_message = f"📊 {symbol}\n{signal}"
                    print(full_message)
                    send_to_telegram(full_message)
            except Exception as e:
                print(f"Fel med {symbol}: {e}")

        time.sleep(3600)  # Kör varje timme

if __name__ == "__main__":
    run_bot()
