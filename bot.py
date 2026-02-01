import time
import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
AFFILIATE_ID = os.getenv("AFFILIATE_ID")

SLEEP_SECONDS = 300  # 5 minutos

def log(msg):
    print(msg, flush=True)

def enviar(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": False
    })
    log(f"[telegram] status={r.status_code}")
    return r.status_code == 200

def buscar_oferta():
    url = "https://api.mercadolibre.com/trends/MLB"
    r = requests.get(url, timeout=15)
    log(f"[ml] status={r.status_code}")

    if r.status_code != 200:
        return None

    data = r.json()
    if not data:
        return None

    item = data[0]

    titulo = item.get("keyword", "Oferta Mercado Livre")
    link = f"https://www.mercadolivre.com.br/{titulo.replace(' ', '-')}_JM?matt_word={AFFILIATE_ID}"

    msg = (
        "🔥 OFERTA EM ALTA NO MERCADO LIVRE 🔥\n\n"
        f"🛒 {titulo}\n\n"
        f"👉 {link}"
    )
    return msg

def main():
    log("🤖 Bot iniciado com sucesso")

    while True:
        try:
            oferta = buscar_oferta()
            if oferta:
                enviar(oferta)
            else:
                log("Nenhuma oferta encontrada")
            log(f"⏳ Dormindo {SLEEP_SECONDS}s...")
            time.sleep(SLEEP_SECONDS)
        except Exception as e:
            log(f"❌ ERRO: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
