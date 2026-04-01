# AI Movie Suggester - Projekt do OS/Sítě

## Popis
Aplikace doporučuje filmy na základě žánru pomocí lokálního LLM.

## Technické údaje
- **Port:** 80 (HTTP)
- **Firewall:** Povoleno TCP 80
- **LLM:** Ollama (model llama3.2:1b)

## Endpointy
- `GET /ping`: Vrátí "pong"
- `GET /status`: Vrátí JSON s informacemi o stavu
- `POST /ai`: Přijímá JSON `{"genre": "sci-fi"}` a vrací doporučení

## Spuštění
1. Ujisti se, že ti běží Ollama s modelem: `ollama run llama3.2:1b`
2. `docker compose up --build`

## Ukázkový příkaz (CURL)
```bash
curl -X POST http://localhost/ai -H "Content-Type: application/json" -d "{\"genre\":\"komedie\"}"