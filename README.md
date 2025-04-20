# Trading Bot

En automatisk tradingbot som analyserar valutapar, kryptovalutor och aktier med SMA-signaler. Skickar köp/sälj + TP/SL till Telegram varje 15:e minut.

## Setup

1. Klona repot
2. Lägg till `.env` med dina API-nycklar
3. Installera beroenden: `pip install -r requirements.txt`
4. Kör boten: `python trading_bot_render.py`

Botten är optimerad för att köras som en Render **background worker**.
