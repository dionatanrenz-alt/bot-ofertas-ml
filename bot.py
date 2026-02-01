import os
import time
import requests

# ====== Variáveis de ambiente (Render) ======
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()
AFFILIATE_ID = os.getenv("AFFILIATE_ID", "").strip()

# ====== Configurações ======
INTERVALO_SEGUNDOS = 300  # 5 minutos
CATEGORIA = "MLB1055"     # Ex.: Eletrônicos (você pode trocar depois)
LIMIT = 1

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

# Guarda último item enviado para não repetir
ultimo_id_enviado = None


def log(msg: str):
    print(msg, flush=True)


def validar_env():
    ok = True
    if not TELEGRAM_TOKEN:
        log("❌ Faltando TELEGRAM_TOKEN nas Environment Variables do Render")
        ok = False
    if not CHAT_ID:
        log("❌ Faltando CHAT_ID nas Environment Variables do Render")
        ok = False
    if not AFFILIATE_ID:
        log("❌ Faltando AFFILIATE_ID nas Environment Variables do Render")
        ok = False
    return ok


def enviar_telegram(texto: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": texto,
        "disable_web_page_preview": False
    }

    try:
        r = requests.post(url, data=data, timeout=25)
        log(f"[telegram] status={r.status_code} resp={r.text[:200]}")
        return r.status_code == 200
    except Exception as e:
        log(f"[telegram] ERRO: {e}")
        return False


def montar_link_afiliado(permalink: str) -> str:
    # Se não tiver AFFILIATE_ID, manda link normal
    if not AFFILIATE_ID:
        return permalink

    # Adiciona matt_word corretamente (com ? ou &)
    sep = "&" if "?" in permalink else "?"
    return f"{permalink}{sep}matt_word={AFFILIATE_ID}"


def buscar_oferta():
    """
    Busca 1 item da categoria (ordenado por preço asc).
    Retorna dict com info da oferta ou None.
    """
    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {
        "category": CATEGORIA,
        "sort": "price_asc",
        "limit": LIMIT
    }

    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=25)
        log(f"[ml] status={r.status_code}")

        # Se Mercado Livre bloquear (403) ou der erro, não derruba o bot
        if r.status_code != 200:
            log(f"[ml] resposta curta: {r.text[:200]}")
            return None

        data = r.json()
        results = data.get("results", [])
        if not results:
            return None

        p = results[0]
        item_id = p.get("id")
        title = p.get("title", "Sem título")
        price = p.get("price", "N/A")
        permalink = p.get("permalink", "")

        link = montar_link_afiliado(permalink)

        return {
            "id": item_id,
            "title": title,
            "price": price,
            "link": link
        }

    except Exception as e:
        log(f"[ml] ERRO: {e}")
        return None


def formatar_mensagem(oferta: dict) -> str:
    return (
        "🔥 OFERTA MERCADO LIVRE\n\n"
        f"📦 {oferta['title']}\n"
        f"💰 R$ {oferta['price']}\n\n"
        f"👉 {oferta['link']}"
    )


def main():
    global ultimo_id_enviado

    log("✅ Bot iniciado com sucesso")

    if not validar_env():
        # Não adianta rodar se faltou env
        log("❌ Corrija as Environment Variables e faça Deploy novamente.")
        return

    # Mensagem de teste (você disse que chegou — ótimo)
    enviar_telegram("✅ Bot online no Render! (mensagem de teste)")

    while True:
        try:
            oferta = buscar_oferta()

            if oferta is None:
                log("Nenhuma oferta encontrada (ou ML bloqueou).")
            else:
                # Evita repetir o mesmo produto sempre
                if oferta["id"] != ultimo_id_enviado:
                    msg = formatar_mensagem(oferta)
                    enviado = enviar_telegram(msg)
                    if enviado:
                        ultimo_id_enviado = oferta["id"]
                else:
                    log("Oferta repetida (mesmo ID). Não enviei de novo.")

            log(f"⏳ Dormindo {INTERVALO_SEGUNDOS}s...")
            time.sleep(INTERVALO_SEGUNDOS)

        except Exception as e:
            log(f"❌ ERRO no loop: {e}")
            time.sleep(30)


if __name__ == "__main__":
    main()
