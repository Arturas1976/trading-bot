import yfinance as yf
import pandas as pd
import ta
import requests
import time
import os

# Telegram duomenys iš aplinkos kintamųjų
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
group_chat_id = os.getenv('GROUP_CHAT_ID')

# Siųsti pranešimą į Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    data = {"chat_id": group_chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Klaida siunčiant žinutę: {e}")

# Gauti signalą iš indikatorių
def generate_signal(df):
    if df is None or df.empty:
        return "⚠️ Duomenų nėra."

    close = df['Close']

    # RSI
    df['RSI'] = ta.momentum.RSIIndicator(close, window=14).rsi()

    # MACD
    macd = ta.trend.MACD(close)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    # MA20
    df['MA20'] = ta.trend.SMAIndicator(close, window=20).sma_indicator()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()

    latest = df.iloc[-1]

    signals = []

    # RSI
    if latest['RSI'] < 30:
        signals.append('🔵 RSI: PIRKTI (RSI < 30)')
    elif latest['RSI'] > 70:
        signals.append('🔴 RSI: PARDUOTI (RSI > 70)')

    # MACD crossover
    if latest['MACD'] > latest['MACD_signal']:
        signals.append('🔵 MACD: Bullish (MACD > Signal)')
    else:
        signals.append('🔴 MACD: Bearish (MACD < Signal)')

    # Kaina žemiau BB
    if latest['Close'] < latest['BB_lower']:
        signals.append('🔵 Kaina žemiau Bollinger Bands → galimas pirkimo taškas')
    elif latest['Close'] > latest['BB_upper']:
        signals.append('🔴 Kaina virš Bollinger Bands → galimas pardavimo taškas')

    return '\n'.join(signals) if signals else "🟡 Nėra aiškaus signalo"

# Testinė žinutė kai botas startuoja
send_telegram_message("✅ Botas paleistas! Tikriname rinkas...")

# Simboliai
symbols = ['BTC-USD', 'ETH-USD', 'AAPL', 'SOL-USD', 'EURUSD=X', 'TSLA', 'GC=F']

while True:
    for symbol in symbols:
        try:
            df = yf.download(symbol, interval="1h", period="2d")
            signal = generate_signal(df)
            send_telegram_message(f"📊 {symbol} signalas:\n{signal}")
        except Exception as e:
            send_telegram_message(f"⚠️ Klaida tikrinant {symbol}: {e}")
    time.sleep(3600)  # Kartojam kas 1 valandą
