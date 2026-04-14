import os # Knihovna pro přístup k operačnímu systému (proměnné prostředí)
import requests # Knihovna pro odesílání HTTP požadavků na AI API
import datetime # Knihovna pro práci s datem a časem
import urllib3 # Knihovna pro síťovou komunikaci
import time # Knihovna pro práci s časem (pauzy)
from flask import Flask, request, jsonify, render_template # Framework pro tvorbu webového serveru
from dotenv import load_dotenv # Načítání tajných údajů ze souboru .env
from sqlalchemy import create_engine, text # Nástroje pro práci s SQL databází

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Vypnutí varování ohledně SSL certifikátů
load_dotenv() # Načtení konfiguračních proměnných z .env

app = Flask(__name__) # Vytvoření instance Flask aplikace

# --- DATABÁZE ---
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://student:heslo123@db:5432/myapp") # Získání adresy k databázi
engine = create_engine(DATABASE_URL) # Připojení k databázovému stroji

# Retry loop: počkáme, až se DB nastartuje (zkusí se připojit 10x)
for i in range(10):
    try:
        with engine.connect() as conn: # Pokus o spojení
            conn.execute(text("SELECT 1")) # Jednoduchý test funkčnosti databáze
            break # Pokud funguje, vyskočí z cyklu
    except Exception:
        print("Čekám na databázi...") # Pokud nefunguje, vypíše zprávu
        time.sleep(2) # Počká 2 sekundy před dalším pokusem

# Vytvoření tabulky pro dotazy a odpovědi, pokud ještě neexistuje
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS history (
            id SERIAL PRIMARY KEY,
            cas TIMESTAMP,
            zanr VARCHAR(100),
            odpoved TEXT
        )
    """))
    conn.commit() # Potvrzení změn v databázi

# --- KONFIGURACE AI ---
api_key = os.environ.get("OPENAI_API_KEY") # Načtení klíče k AI
base_url = os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1") # Adresa AI serveru

@app.route('/') # Definice hlavní stránky
def index():
    return render_template('index.html') # Zobrazení tvého HTML souboru

@app.route('/status', methods=['GET']) # Endpoint pro kontrolu, zda server běží
def status():
    return jsonify({
        "status": "running",
        "autor": "Monika Němečková",
        "cas": datetime.datetime.now().isoformat(),
        "projekt": "Movie AI Suggestion with DB"
    })

@app.route('/history', methods=['GET']) # Endpoint pro získání historie z DB
def get_history():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT zanr, odpoved FROM history ORDER BY cas DESC LIMIT 10")) # Vybere posledních 10 záznamů
            history_data = [{"zanr": row[0], "odpoved": row[1]} for row in result] # Převede výsledky na seznam
            return jsonify(history_data) # Pošle historii jako JSON do prohlížeče
    except Exception as e:
        return jsonify({"error": str(e)}), 500 # Vrátí chybu, pokud se čtení nepovedlo

@app.route('/ai', methods=['POST']) # Hlavní endpoint pro dotaz na AI
def ai():
    data = request.json # Přijme data z prohlížeče (ten žánr)
    genre = data.get("genre", "akční") # Získá žánr, nebo použije "akční" jako základ
    
    prompt = f"Doporuč jeden nejlepší film pro žánr {genre}. Odpověz pouze jednou krátkou větou v češtině." # Zadání pro AI
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"} # Nastavení autorizace
    payload = { # Balíček dat, který se posílá AI
        "model": "gemma3:27b", 
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        clean_url = base_url.rstrip('/') # Odstranění lomítka na konci adresy
        target_url = f"{clean_url}/chat/completions" # Sestavení cílové adresy pro dotaz
        
        response = requests.post(target_url, headers=headers, json=payload, timeout=20, verify=False) # Odeslání dotazu AI
        
        if response.status_code == 200: # Pokud AI odpověděla správně
            ai_response = response.json()['choices'][0]['message']['content'].strip() # Vytažení textu odpovědi
            
            with engine.connect() as conn: # Uložení dotazu do databáze
                conn.execute(
                    text("INSERT INTO history (cas, zanr, odpoved) VALUES (:cas, :zanr, :odpoved)"),
                    {"cas": datetime.datetime.now(), "zanr": genre, "odpoved": ai_response}
                )
                conn.commit() # Potvrzení uložení
            
            return jsonify({"doporuceni": ai_response}) # Poslání výsledku zpět do prohlížeče
        else:
            return jsonify({"error": f"Server vrátil {response.status_code}."}), response.status_code # Chyba na straně AI

    except Exception as e:
        return jsonify({"error": f"Spojení selhalo: {str(e)}"}), 500 # Chyba v komunikaci nebo v kódu

if __name__ == "__main__": # Spuštění serveru
    port = int(os.environ.get("PORT", 5000)) # Nastavení portu (standardně 5000)
    app.run(host='0.0.0.0', port=port) # Spuštění aplikace na všech dostupných adresách
