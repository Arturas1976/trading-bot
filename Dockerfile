# Välj en officiell Python-bild som bas
FROM python:3.11-slim

# Kopiera projektfiler till containern
COPY . /app

# Sätt arbetskatalogen
WORKDIR /app

# Installera Python-bibliotek
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Starta boten
CMD ["python", "trading_bot_render.py"]
