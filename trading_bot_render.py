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

# Top 20 kryptovalutor (CoinMarketCap)
CRYPTO_SYMBOLS = [
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", 
    "AVAX", "DOT", "LINK", "MATIC", "SHIB", "TON", 
    "DAI", "LTC", "UNI", "ATOM", "XMR", "ETC", "FIL"
]

# Simulerad RSI/MACD-strategi (ersätt med riktig logik!)
def generate_signal(symbol):
    # Simulera RSI (30-70) och MACD-crossover
    rsi = random.uniform(30, 70)
    macd = random.choice(["BULLISH", "BEARISH", "NEUTRAL"])
    
    if rsi < 40 and macd == "BULLISH":
        action = "KÖP"
        entry_price = round(random.uniform(1, 100000), 2)  # Pris i USDT
        take_profit = round(entry_price * 1.03, 2)  # +3%
        stop_loss = round(entry_price * 0.98, 2)    # -2%
    elif rsi > 60 and macd == "BEARISH":
        action = "SLUTA"
        entry_price = round(random.uniform(1, 100000), 2)
        take_profit = round(entry_price * 0.97, 2)  # -3%
        stop_loss = round(entry_price * 1.02, 2)    # +2%
    else:
        return None  # Ingen signal
    
    return (
        f"📈 **{symbol}/USDT**\n"
        f"🔄 RSI: {round(rsi, 2)}, MACD: {macd}\n"
        f"🚀 {action} @ {entry_price}\n"
        f"🎯 Take-Profit: {take_profit}\n"
        f"🛑 Stop-Loss: {stop_loss}\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    )

# Skicka automatsignaler var 15:e minut
async def send_auto_signals(context: ContextTypes.DEFAULT_TYPE):
    for symbol in CRYPTO_SYMBOLS:
        signal = generate_signal(symbol)
        if signal:
            await context.bot.send_message(
                chat_id=context.job.chat_id,
                text=signal,
                parse_mode="Markdown"
            )

# Startkommando + aktivera auto-signaler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Kryptoboten är nu igång!**\n"
        "🔔 Du kommer få signaler var 15:e minut.\n"
        f"📡 Övervakar: {', '.join(CRYPTO_SYMBOLS[:5])}..."
    )
    # Schemalägg auto-signaler
    context.job_queue.run_repeating(
        send_auto_signals,
        interval=900,  # 15 minuter i sekunder
        first=10,      # Första meddelandet efter 10 sek
        chat_id=update.effective_chat.id
    )

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        logger.error("❌ Sätt TELEGRAM_TOKEN i miljövariabler!")
        return

    # Bygg boten (v20+ syntax)
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Lägg till kommandon
    application.add_handler(CommandHandler("start", start))
    
    logger.info("Boten startar med RSI/MACD-strategi...")
    application.run_polling()

if __name__ == "__main__":
    main()
