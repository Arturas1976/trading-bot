import yfinance as yf
import time
import requests
import os
import pandas as pd
import ta

# Gauti duomenis iš Environment Variables
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Tavo Telegram bot token
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')   # Tavo Telegram grupės chat ID (pvz. -1001234567890)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    data = {
        "chat_id": GROUP_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data)
        if not response.ok:
            print("❌ Klaida siunčiant į Telegram:", response.text)
    except Exception as e:
        print("❌ Išimtis:", e)

def analyze_market(symbol):
    try:
        df = yf.download(symbol, period="7d", interval="15m")
        if df.empty or len(df) < 100:
            return

        df.dropna(inplace=True)

        # RSI
        rsi = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        last_rsi = rsi.iloc[-1]

        # Moving Average
        ma = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
        last_ma = ma.iloc[-1]

        # MACD
        macd = ta.trend.MACD(df['Close'])
        macd_val = macd.macd_diff().iloc[-1]

        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['Close'])
        upper = bb.bollinger_hband().iloc[-1]
        lower = bb.bollinger_lband().iloc[-1]
        close_price = df['Close'].iloc[-1]

        message = f"📊 <b>{symbol}</b>\n"
        message += f"📉 RSI: {last_rsi:.2f}\n"
        message += f"📈 MA(20): {last_ma:.2f}\n"
        message += f"📊 MACD Diff: {macd_val:.4f}\n"
        message += f"📎 Bollinger: {lower:.2f} - {upper:.2f}\n"
        message += f"💰 Kaina: {close_price:.2f}\n"

        signal = None
        if last_rsi < 30:
            signal = "🟢 <b>PIRKTI</b> (RSI < 30)"
        elif last_rsi > 70:
            signal = "🔴 <b>PARDUOTI</b> (RSI > 70)"

        if signal:
            message += f"\n🚨 SIGNALAS: {signal}"

        send_telegram_message(message)

    except Exception as e:
        print(f"Klaida su {symbol}: {e}")

def main():
    send_telegram_message("✅ <b>Trading botas paleistas!</b>\nTikrinam rinkas kas 15 min...")

    symbols = [
    "BTC-USD", "ETH-USD", "SOL-USD",
    "AAPL", "TSLA", "MSFT",
    "EURUSD=X", "GBPUSD=X", "GC=F"  # Pakeistas auksas
]

    while True:
        for symbol in symbols:
            analyze_market(symbol)
        time.sleep(900)  # 15 min (900 sek)

if __name__ == "__main__":
    main()
