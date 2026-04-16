import os
import requests
import datetime
import urllib3
import time
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://student:heslo123@db:5432/myapp")
engine = create_engine(DATABASE_URL)

for i in range(10):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            break
    except Exception:
        print("Čekám na databázi...")
        time.sleep(2)

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS history (
            id SERIAL PRIMARY KEY,
            cas TIMESTAMP,
            zanr VARCHAR(100),
            odpoved TEXT
        )
    """))
    conn.commit()

api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("OPENAI_BASE_URL", "https://ithope.eu")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "running",
        "autor": "Monika Němečková",
        "cas": datetime.datetime.now().isoformat(),
        "projekt": "Movie AI Suggestion with DB"
    })

@app.route('/history', methods=['GET'])
def get_history():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT zanr, odpoved FROM history ORDER BY cas DESC LIMIT 10"))
            history_data = [{"zanr": row[0], "odpoved": row[1]} for row in result]
            return jsonify(history_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ai', methods=['POST'])
def ai():
    data = request.json
    genre = data.get("genre", "akční")
    
    prompt = f"Doporuč jeden nejlepší film pro žánr {genre}. Odpověz pouze jednou krátkou větou v češtině."
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gemma3:27b", 
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        clean_url = base_url.rstrip('/')
        target_url = f"{clean_url}/chat/completions"
        
        response = requests.post(target_url, headers=headers, json=payload, timeout=20, verify=False)
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content'].strip()
            
            with engine.connect() as conn:
                conn.execute(
                    text("INSERT INTO history (cas, zanr, odpoved) VALUES (:cas, :zanr, :odpoved)"),
                    {"cas": datetime.datetime.now(), "zanr": genre, "odpoved": ai_response}
                )
                conn.commit()
            
            return jsonify({"doporuceni": ai_response})
        else:
            return jsonify({"error": f"Server vrátil {response.status_code}."}), response.status_code

    except Exception as e:
        return jsonify({"error": f"Spojení selhalo: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
