import time
import requests
import os

# =========================
# VARIÁVEIS DE AMBIENTE
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
AFFILIATE_ID = os.getenv("AFFILIATE_ID")  # ex: promotop1

# =========================
# HEADERS (OBRIGATÓRIO ML)
# =========================
HEADERS = {
    "User-Agent": "dionatanrenzz-bot/1.0",
    "Accept": "application/json"
}

# =========================
# LOG SIMPLES
# =========================
def log(msg):
    print(msg, flush=True)

# =========================
# ENVIAR TELEGRAM
# =========================
def enviar(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": False
    })
    log(f"[telegram] status={r.status_code}")
    return r.status_code == 200

# =========================
# BUSCAR OFERTA ML
# =========================
def buscar_oferta():
    url = "https://api.mercadolibre.com/sites/MLB/search"

    params = {
        "category": "MLB1055",   # Eletrônicos
        "sort": "price_asc",
        "limit": 1
    }

    r = requests.get(url, params=params, headers=HEADERS)
    log(f"[ml] status={r.status_code}")

    if r.status_code != 200:
        return None

    data = r.json()

    if "results" not in data or len(data["results"]) == 0:
        log("Nenhuma oferta encontrada")
        return None

    p = data["results"][0]

    link = f"{p['permalink']}?matt_word={AFFILIATE_ID}"

    msg = (
        f"🔥 OFERTA MERCADO LIVRE 🔥\n\n"
        f"🛒 {p['title']}\n"
        f"💰 R$ {p['price']}\n\n"
        f"👉 {link}"
    )

    return msg

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    log("🤖 Bot iniciado com sucesso")
    enviar("✅ Bot online e funcionando!")

    while True:
        try:
            oferta = buscar_oferta()
            if oferta:
                enviar(oferta)

            log("⏳ Dormindo 300s...")
            time.sleep(300)

        except Exception as e:
            log(f"❌ ERRO: {e}")
            time.sleep(30)
