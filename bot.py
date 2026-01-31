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
        "category": "MLB1055",
        "sort": "price_asc",
        "limit": 1
    }

    r = requests.get(url, params=params)
    log(f"[ml] status={r.status_code}")
    data = r.json()

    results = data.get("results", [])
    if not results:
        log("[ml] sem resultados")
        return None

    p = results[0]
    link = f"{p['permalink']}?matt_word={AFFILIATE_ID}"

    msg = (
        f"🔥 OFERTA 🔥\n\n"
        f"📦 {p.get('title')}\n"
        f"💰 R$ {p.get('price')}\n\n"
        f"👉 COMPRAR AGORA:\n{link}"
    )
    return msg

# ===== TESTE AO INICIAR =====
log("=== BOT INICIANDO ===")
log(f"TELEGRAM_TOKEN definido? {'sim' if TELEGRAM_TOKEN else 'nao'}")
log(f"CHAT_ID={CHAT_ID}")
log(f"AFFILIATE_ID={AFFILIATE_ID}")

if TELEGRAM_TOKEN and CHAT_ID and AFFILIATE_ID:
    enviar("✅ Bot iniciou no Render! Teste de envio OK.")
else:
    log("❌ FALTAM VARIÁVEIS DE AMBIENTE")

# ===== LOOP =====
while True:
    try:
        oferta = buscar_oferta()
        if oferta:
            enviar(oferta)
        else:
            log("[bot] nenhuma oferta enviada neste ciclo")
    except E
