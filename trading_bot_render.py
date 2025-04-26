import os
import logging
import time
import random
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Loggning
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Top 20 kryptovalutor (för RSI/MACD-analys)
CRYPTO_SYMBOLS = [
    "BTC", "ETH", "BNB", "SOL", "XRP",
    "ADA", "DOGE", "AVAX", "DOT", "LINK",
    "MATIC", "SHIB", "TON", "DAI", "LTC",
    "UNI", "ATOM", "XMR", "ETC", "FIL"
]

# Simulerad RSI/MACD-strategi (ersätt med din egen logik!)
def check_rsi_macd(symbol):
    # Simulerar RSI (överköpt/översålt) och MACD-crossover
    rsi = random.uniform(30, 70)  # RSI mellan 30-70
    macd_crossover = random.choice(["BULLISH", "BEARISH", "NEUTRAL"])
    
    if rsi < 40 and macd_crossover == "BULLISH":
        return "BUY"
    elif rsi > 60 and macd_crossover == "BEARISH":
        return "SELL"
    else:
        return None

# Generera signal med Stop-Loss/Take-Profit
def generate_signal(symbol):
    action = check_rsi_macd(symbol)
    if not action:
        return None
    
    entry_price = round(random.uniform(1, 100), 2)  # Ersätt med API-pris
    if action == "BUY":
        take_profit = round(entry_price * 1.03, 2)  # +3%
        stop_loss = round(entry_price * 0.98, 2)    # -2%
    else:
        take_profit = round(entry_price * 0.97, 2)  # -3%
        stop_loss = round(entry_price * 1.02, 2)     # +2%
    
    return (
        f"📈 **{symbol}/USDT**: {action} @ {entry_price}\n"
        f"🎯 Take-Profit: {take_profit}\n"
        f"🛑 Stop-Loss: {stop_loss}\n"
        f"⏳ Tid: {datetime.now().strftime('%H:%M')}"
    )

# Skicka signaler till användare (var 15:e minut)
def send_auto_signals(context: CallbackContext):
    for symbol in CRYPTO_SYMBOLS:
        signal = generate_signal(symbol)
        if signal:
            context.bot.send_message(
                chat_id=context.job.context,
                text=signal,
                parse_mode="Markdown"
            )

# Kommandon
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.job_queue.run_repeating(
        send_auto_signals,
        interval=900,  # 15 minuter i sekunder
        first=0,
        context=chat_id
    )
    update.message.reply_text("🔔 **Automatiska kryptosignaler aktiverade!**")

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        logger.error("❌ Sätt TELEGRAM_TOKEN i miljövariabler!")
        return

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Kommandon
    dispatcher.add_handler(CommandHandler("start", start))

    logger.info("Boten startar med RSI/MACD-strategi...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
