FROM python:3.12-slim # Jako základ použije lehkou verzi Pythonu 3.12 (operační systém pro kontejner)
WORKDIR /app # Vytvoří v kontejneru pracovní složku /app a přepne se do ní

# Instalace závislostí
COPY requirements.txt . # Zkopíruje seznam knihoven z tvého PC do kontejneru
RUN pip install --no-cache-dir -r requirements.txt # Spustí instalaci všech knihoven ze seznamu

# Kopírování zbytku aplikace
COPY . . # Zkopíruje úplně všechny ostatní soubory (tvůj kód, HTML atd.) do kontejneru

# Spuštění aplikace
CMD ["python", "app.py"] # Hlavní příkaz, který spustí tvůj server, když kontejner nastartuje
