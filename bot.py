import time
import requests
import os

# =========================
# VARIÁVEIS DE AMBIENTE
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
AFFILIATE_ID = os.getenv("AFFILIATE_ID")
SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", "300"))  # padrão 5 min

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# =========================
# FUNÇÕES
# =========================
def log(msg):
    print(msg, flush=True)

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": False
    }
    try:
        r = requests.post(url, data=payload, timeout=10)
        log(f"[telegram] status={r.status_code}")
    except Exception as e:
        log(f"[telegram] erro: {e}")

def buscar_oferta():
    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {
        "category": "MLB1055",  # eletrônicos
        "sort": "price_asc",
        "limit": 1
    }

    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        log(f"[ml] status={r.status_code}")

        if r.status_code != 200:
            return None

        data = r.json()
        if "results" not in data or len(data["results"]) == 0:
            return None

        p = data["results"][0]
        link = f"{p['permalink']}?matt_word={AFFILIATE_ID}"

        msg = (
            "🔥 OFERTA MERCADO LIVRE 🔥\n\n"
            f"📦 {p['title']}\n"
            f"💰 R$ {p['price']}\n\n"
            f"👉 {link}"
        )
        return msg

    except Exception as e:
        log(f"[ml] erro: {e}")
        return None

# =========================
# LOOP PRINCIPAL
# =========================
log("🤖 Bot iniciado com sucesso")

while True:
    try:
        oferta = buscar_oferta()
        if oferta:
            enviar_telegram(oferta)
        else:
            log("Nenhuma oferta encontrada")

        log(f"⏳ Dormindo {SLEEP_SECONDS}s...")
        time.sleep(SLEEP_SECONDS)

    except Exception as e:
        log(f"❌ ERRO NO LOOP: {e}")
        time.sleep(30)
