# Välj en officiell Python-bild som bas
FROM python:3.11-slim

# Uppdatera systemet och installera systemberoenden
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libatlas-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    && apt-get clean

# Installera TA-Lib
RUN wget https://github.com/markusliebelt/ta-lib/releases/download/v0.4.0/ta-lib-0.4.0-src.tar.gz \
    && tar -xvf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib-0.4.0 && ./configure && make && make install \
    && cd .. && rm -rf ta-lib-0.4.0 ta-lib-0.4.0-src.tar.gz

# Skapa och aktivera en virtuell miljö
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Kopiera projektfiler till containern
COPY . /app

# Sätt arbetskatalogen
WORKDIR /app

# Installera Python-bibliotek
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Starta boten
CMD ["python", "trading_bot_render.py"]
