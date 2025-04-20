import yfinance as yf
import ta
import time
import requests
from datetime import datetime

# === TELEGRAM DUOMENYS (ĮRAŠYK SAVO) ===
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

# === INSTRUMENTAI ===
symbols = [
    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "AVAX-USD",
    "AAPL", "MSFT", "GOOG", "AMZN", "META", "TSLA", "NVDA",
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCHF=X", "USDCAD=X",
    "GC=F", "SI=F", "CL=F", "HG=F", "PL=F", "PA=F"
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram klaida:", e)

def analyze(symbol):
    try:
        df = yf.download(symbol, period="2d", interval="1h")
        if df.empty or len(df) < 50:
            return None

        df = df.dropna()
        close = df['Close']

        # RSI
        rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]

        # MA
        ma50 = close.rolling(50).mean().iloc[-1]
        ma200 = close.rolling(200).mean().iloc[-1]

        # MACD
        macd = ta.trend.MACD(close)
        macd_line = macd.macd().iloc[-1]
        signal_line = macd.macd_signal().iloc[-1]

        # Bollinger
        bb = ta.volatility.BollingerBands(close)
        bb_upper = bb.bollinger_hband().iloc[-1]
        bb_lower = bb.bollinger_lband().iloc[-1]

        price = close.iloc[-1]
        signal = None

        if rsi < 30 and price < bb_lower and macd_line > signal_line:
            signal = "📈 PIRKTI"
        elif rsi > 70 and price > bb_upper and macd_line < signal_line:
            signal = "📉 PARDUOTI"

        if signal:
            sl = round(price * 0.97, 2)
            tp = round(price * 1.05, 2)
            msg = f"""
📊 {symbol}
Signalas: {signal}
Kaina: {price:.2f}
RSI: {rsi:.2f}
MA50: {ma50:.2f}
MA200: {ma200:.2f}
MACD: {macd_line:.2f} / {signal_line:.2f}
Bollinger: [{bb_lower:.2f} - {bb_upper:.2f}]
SL: {sl} | TP: {tp}
Laikas: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
            send_telegram_message(msg)

    except Exception as e:
        print(f"Klaida analizėje {symbol}: {e}")

while True:
    for symbol in symbols:
        analyze(symbol)
        time.sleep(2)
    print("🔁 Atnaujinimas baigtas, laukiama 1 valanda...")
    time.sleep(3600)
