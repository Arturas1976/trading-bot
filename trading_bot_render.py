import os
import logging
import random
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
)

# Loggning
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

CRYPTO_SYMBOLS = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "AVAX", "DOT", "LINK"]

import requests  # Lägg till denna import

def get_real_price(symbol):
    """Hämta riktigt pris från Binance API"""
    try:
        response = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT")
        data = response.json()
        return float(data["price"])
    except Exception as e:
        logger.error(f"Kunde inte hämta pris för {symbol}: {e}")
        return None

def generate_signal(symbol):
    rsi = random.uniform(30, 70)
    macd = random.choice(["BULLISH", "BEARISH", "NEUTRAL"])
    
    # Hämta riktigt pris från Binance
    entry_price = get_real_price(symbol)
    if not entry_price:
        return None  # Om API-anropet misslyckas
    
    if rsi < 40 and macd == "BULLISH":
        action = "KÖP"
        take_profit = round(entry_price * 1.03, 2)
        stop_loss = round(entry_price * 0.98, 2)
    elif rsi > 60 and macd == "BEARISH":
        action = "SÄLJ"
        take_profit = round(entry_price * 0.97, 2)
        stop_loss = round(entry_price * 1.02, 2)
    else:
        return None
    
    return (
        f"📈 **{symbol}/USDT**\n"
        f"🚀 {action} @ {entry_price}\n"
        f"🎯 Take-Profit: {take_profit}\n"
        f"🛑 Stop-Loss: {stop_loss}\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    )

async def send_auto_signals(context: ContextTypes.DEFAULT_TYPE):
    for symbol in CRYPTO_SYMBOLS:
        signal = generate_signal(symbol)
        if signal:
            await context.bot.send_message(
                chat_id=context.job.chat_id,
                text=signal,
                parse_mode="Markdown"
            )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Kryptoboten är nu igång!**\n"
        "🔔 Du kommer få signaler var 1 timme."
    )
    
    # Kontrollera att job_queue finns
    if not context.job_queue:
        await update.message.reply_text("⚠️ JobQueue är inte aktiverad. Kontrollera installationen.")
        return
    
    context.job_queue.run_repeating(
        send_auto_signals,
        interval=3600,  # 3600 sekunder = 1 timme
        first=10,
        chat_id=update.effective_chat.id
    )

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        logger.error("❌ Sätt TELEGRAM_TOKEN i miljövariabler!")
        return

    # Bygg applikationen med JobQueue
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )
    
    application.add_handler(CommandHandler("start", start))
    
    logger.info("Boten startar...")
    application.run_polling()

if __name__ == "__main__":
    main()
