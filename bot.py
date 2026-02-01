import time
import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
AFFILIATE_ID = os.getenv("AFFILIATE_ID")

def log(msg):
    print(msg, flush=True)

def enviar(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    log(f"[telegram] status={r.status_code} resp={r.text[:200]}")
    return r.status_code == 200

def buscar_oferta():
    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {
        "category": "MLB1055",  # Eletrônicos
        "sort": "price_asc",
        "limit": 1
    }

    r = requests.get(url, params=params)
    data = r.json()

    if "results" not in data or not data["results"]:
        log("Nenhuma oferta encontrada")
        return None

    p = data["results"][0]
    link = f"{p['permalink']}?matt_word={AFFILIATE_ID}"

    msg = (
        f"🔥 OFERTA MERCADO LIVRE 🔥\n\n"
        f"{p['title']}\n"
        f"💰 R$ {p['price']}\n\n"
        f"👉 {link}"
    )

    return msg

log("🚀 Bot iniciado com sucesso")

while True:
    try:
        oferta = buscar_oferta()
        if oferta:
            enviar(oferta)
        time.sleep(300)  # 5 minutos
    except Exception as e:
        log(f"ERRO: {e}")
        time.sleep(30)
