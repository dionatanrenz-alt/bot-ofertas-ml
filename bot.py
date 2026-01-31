import time
import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
AFFILIATE_ID = os.getenv("AFFILIATE_ID")

def buscar_oferta():
    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {
        "category": "MLB1055",  # Eletrônicos
        "sort": "price_asc",
        "limit": 1
    }
    r = requests.get(url, params=params).json()
    if "results" not in r or len(r["results"]) == 0:
        return None

    p = r["results"][0]
    link = f"{p['permalink']}?matt_word={AFFILIATE_ID}"

    msg = (
        f"🔥 OFERTA 🔥\n\n"
        f"📦 {p['title']}\n"
        f"💰 R$ {p['price']}\n\n"
        f"👉 COMPRAR AGORA:\n{link}"
    )
    return msg

def enviar(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

while True:
    oferta = buscar_oferta()
    if oferta:
        enviar(oferta)
    time.sleep(300)  # 5 minutos
