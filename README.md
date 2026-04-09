# Movie AI Suggestion 🎬

Tato webová aplikace postavená na frameworku **Flask** slouží k rychlému doporučení nejlepšího filmu na základě uživatelem zadaného žánru. Aplikace využívá umělou inteligenci (model **Gemma 3**) skrze API školního proxy serveru.

---

## 🚀 Funkce
* **Doporučení filmu:** Uživatel zadá žánr a získá jednu konkrétní doporučenou pecku od AI.
* **Status Endpoint:** `/status` vrací informace o běžící aplikaci, autorovi a čase.
* **Responzivní rozhraní:** Jednoduché a funkční webové prostředí.

## 🛠️ Technologie
* **Backend:** Python 3.10+
* **Framework:** Flask
* **AI Model:** Gemma 3:27b (kompatibilní s OpenAI standardem)
* **Knihovny:** `requests` pro komunikaci s API, `python-dotenv` pro správu klíčů.

## 📦 Instalace a spuštění

1.  **Příprava prostředí:**
    Ujisti se, že máš nainstalovaný Python a potřebné knihovny:
    ```bash
    pip install flask requests python-dotenv urllib3
    ```

2.  **Konfigurace:**
    V kořenovém adresáři projektu vytvoř soubor `.env` a vlož do něj potřebné údaje (klíč doplň podle instrukcí učitele):
    ```env
    OPENAI_API_KEY=tvuj_api_klic
    OPENAI_BASE_URL=[https://kurim.ithope.eu/v1](https://kurim.ithope.eu/v1)
    ```

3.  **Spuštění aplikace:**
    Spusť hlavní skript:
    ```bash
    python app.py
    ```
    Aplikace bude dostupná v prohlížeči na adrese `http://localhost:80`.

## 🔌 API Endpointy

| Metoda | Endpoint | Popis |
| :--- | :--- | :--- |
| **GET** | `/` | Hlavní uživatelské rozhraní. |
| **GET** | `/status` | Diagnostika aplikace (JSON formát). |
| **POST** | `/ai` | Zpracování požadavku na film (bere JSON `{"genre": "..."}`). |

---

## 👩‍💻 Autorka
* **Monika Němečková**

> **Poznámka pro vývojáře:** Z důvodu konfigurace školního serveru je v kódu nastaveno `verify=False` u požadavků na API a vypnuto varování `InsecureRequestWarning`.
