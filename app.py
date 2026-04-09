import os
import requests
import datetime
import urllib3
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Vypne varování o nezabezpečeném HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

app = Flask(__name__)

api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "running",
        "autor": "Monika Němečková",
        "cas": datetime.datetime.now().isoformat(),
        "projekt": "Movie AI Suggestion with Gemini"
    })

@app.route('/ai', methods=['POST'])
def ai():
    data = request.json
    genre = data.get("genre", "akční")
    
    # Prompt upravený pro filmy
    prompt = f"Doporuč jeden nejlepší film pro žánr {genre}. Odpověz pouze jednou krátkou větou v češtině."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Použijeme model gemma3:27b, který máš v kódu i ty, protože na školním serveru běží tento
    payload = {
        "model": "gemma3:27b", 
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        clean_url = base_url.rstrip('/')
        target_url = f"{clean_url}/chat/completions"
        
        
        response = requests.post(
            target_url, 
            headers=headers, 
            json=payload, 
            timeout=20, 
            verify=False
        )
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
           
            return jsonify({"doporuceni": ai_response.strip()})
        else:
            return jsonify({
                "error": f"Server vrátil {response.status_code}.",
                "details": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({"error": f"Spojení selhalo: {str(e)}"}), 500

if __name__ == "__main__":
    # Nastavení portu podle tvého vzoru (flexibilní port pro server)
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=port)
