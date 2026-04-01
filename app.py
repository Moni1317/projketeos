from flask import Flask, request, jsonify, render_template
import requests
import datetime
import os

app = Flask(__name__)

# URL pro Ollama API [cite: 17, 66]
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ping', methods=['GET'])
def ping():
    return "pong"

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "running",
        "autor": "Monika Němečková",
        "cas": datetime.datetime.now().isoformat(),
        "projekt": "Movie AI Suggestion"
    })

@app.route('/ai', methods=['POST'])
def ai():
    data = request.json
    genre = data.get("genre", "akční")
    
    payload = {
        "model": "gemma3:27b", 
        "prompt": f"Doporuč jeden nejlepší film pro žánr {genre}. Odpověz pouze jednou krátkou větou v češtině.",
        "stream": False
    }

    try:
        # Volání lokálního LLM dle zadání [cite: 17, 30]
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response_data = response.json()
        return jsonify({"doporuceni": response_data.get("response", "").strip()})
    except Exception as e:
        return jsonify({"error": f"Ollama není dostupná: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)