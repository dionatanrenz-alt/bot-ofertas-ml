import os
import time
import requests
import traceback

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
AFFILIATE_ID = os.getenv("AFFILIATE_ID")

# Tempo entre envios (segundos). 300 = 5 minutos
SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", "300"))

# Categoria do ML (você pode trocar depois)
# Ex: MLB1055 = eletrônicos (exemplo). Se quiser, depois te ajudo a escolher categoria.
ML_CATEGORY = os.getenv("ML_CATEGORY", "MLB1055")


def log(msg: str):
    print(msg, flush=True)


def enviar_mensagem(texto: str) -> bool:
    if not TELEGRAM_TOKEN or not CHAT_ID:
        raise RuntimeError("TELEGRAM_TOKEN ou CHAT_ID não definidos nas variáveis do Render.")

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "disable_web_page_preview": False,
    }

    r = requests.post(url, data=payload, timeout=20)
    log(f"[telegram] status={r.status_code} resp={r.text[:200]}")
    return r.status_code == 200


def buscar_oferta() -> str | None:
    """
    Busca 1 item no Mercado Livre.
    Retorna a mensagem pronta para enviar no Telegram.
    """
    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {
        "category": ML_CATEGORY,
        "sort": "price_asc",
        "limit": 1,
    }

    r = requests.get(url, params=params, timeout=20)
    log(f"[ml] status={r.status_code}")
    r.raise_for_status()
    data = r.json()

    results = data.get("results", [])
    if not results:
        return None

    p = results[0]

    titulo = p.get("title", "Oferta Mercado Livre")
    preco = p.get("price", "")
    permalink = p.get("permalink", "")

    # Link afiliado (se AFFILIATE_ID estiver vazio, manda o link normal)
    if AFFILIATE_ID and permalink:
        link = f"{permalink}?matt_word={AFFILIATE_ID}"
    else:
        link = permalink

    msg = (
        f"🔥 OFERTA MERCADO LIVRE 🔥\n\n"
        f"📌 {titulo}\n"
        f"💰 R$ {preco}\n\n"
        f"👉 {link}"
    )

    return msg, p.get("id")


def main():
    log("🤖 Bot iniciando...")

    # Teste imediato: envia uma mensagem assim que o bot inicia
    try:
        enviar_mensagem("✅ Bot online! (teste)")
    except Exception:
        log("❌ Falha ao enviar mensagem de teste:")
        log(traceback.format_exc())

    ultimo_id = None

    while True:
        try:
            resultado = buscar_oferta()
            if resultado:
                msg, item_id = resultado

                # Evita repetir a mesma oferta
                if item_id != ultimo_id:
                    enviado = enviar_mensagem(msg)
                    if enviado:
                        ultimo_id = item_id
                else:
                    log("ℹ️ Mesma oferta de antes, não vou repetir.")

            log(f"⏳ Dormindo {SLEEP_SECONDS}s...")
            time.sleep(SLEEP_SECONDS)

        except Exception:
            log("❌ ERRO no loop:")
            log(traceback.format_exc())
            time.sleep(60)


if __name__ == "__main__":
    main()
