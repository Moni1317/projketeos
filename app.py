import os
import datetime
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Konfigurace Gemini API
# Klíč bys měl mít v proměnných prostředí (Environment Variables)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "TVUJ_API_KLIC")
genai.configure(api_key=GEMINI_API_KEY)

# Výběr modelu
model = genai.GenerativeModel('gemini-1.5-flash')

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
    
    prompt = f"Doporuč jeden nejlepší film pro žánr {genre}. Odpověz pouze jednou krátkou větou v češtině."

    try:
        # Generování odpovědi pomocí Gemini
        response = model.generate_content(prompt)
        return jsonify({"doporuceni": response.text.strip()})
    except Exception as e:
        return jsonify({"error": f"Gemini API chyba: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
