import os
import time
import requests
import feedparser

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
FEED_URL = os.getenv("FEED_URL")

LAST_LINK_FILE = "last_link.txt"

def log(msg):
    print(msg, flush=True)

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "disable_web_page_preview": False
    }
    r = requests.post(url, data=payload, timeout=20)
    log(f"[telegram] status={r.status_code} resp={r.text[:200]}")
    return r.status_code == 200

def carregar_ultimo_link():
    try:
        with open(LAST_LINK_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""
    except Exception as e:
        log(f"[last_link] erro lendo arquivo: {e}")
        return ""

def salvar_ultimo_link(link):
    try:
        with open(LAST_LINK_FILE, "w", encoding="utf-8") as f:
            f.write(link)
    except Exception as e:
        log(f"[last_link] erro salvando arquivo: {e}")

def validar_variaveis():
    faltando = []
    if not TELEGRAM_TOKEN:
        faltando.append("TELEGRAM_TOKEN")
    if not CHAT_ID:
        faltando.append("CHAT_ID")
    if not FEED_URL:
        faltando.append("FEED_URL")

    if faltando:
        log("❌ Faltando variáveis de ambiente: " + ", ".join(faltando))
        log("➡️ Vá em Render > Environment e crie essas variáveis.")
        return False

    return True

def buscar_oferta_rss():
    feed = feedparser.parse(FEED_URL)

    # feed.bozo == 1 geralmente significa que teve warning/erro ao parsear
    log(f"[rss] bozo={feed.bozo} entries={len(feed.entries) if feed.entries else 0}")

    if not feed.entries:
        return None

    item = feed.entries[0]
    titulo = getattr(item, "title", "Oferta do Mercado Livre")
    link = getattr(item, "link", "")

    if not link:
        return None

    msg = (
        "🔥 OFERTA MERCADO LIVRE (RSS) 🔥\n\n"
        f"{titulo}\n\n"
        f"👉 {link}"
    )
    return link, msg

def main():
    log("🤖 Iniciando bot RSS...")

    if not validar_variaveis():
        # não fica reiniciando e dando erro toda hora
        time.sleep(3600)
        return

    # Mensagem de teste ao iniciar
    enviar_telegram("✅ Bot RSS ligado no Render! Vou postar ofertas quando aparecerem no feed.")

    ultimo_link = carregar_ultimo_link()
    log(f"[last_link] carregado: {ultimo_link[:80]}")

    while True:
        try:
            resultado = buscar_oferta_rss()
            if resultado:
                link, msg = resultado

                if link != ultimo_link:
                    ok = enviar_telegram(msg)
                    if ok:
                        ultimo_link = link
                        salvar_ultimo_link(link)
                        log("[rss] ✅ nova oferta enviada")
                else:
                    log("[rss] mesma oferta, não enviei")

            log("⏳ Dormindo 300s...")
            time.sleep(300)

        except Exception as e:
            log(f"❌ ERRO no loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
