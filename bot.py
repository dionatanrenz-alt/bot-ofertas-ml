import os
import time
import requests
import feedparser
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

def env(name, default=None, required=False):
    v = os.getenv(name, default)
    if required and (v is None or str(v).strip() == ""):
        raise RuntimeError(f"Falta variável de ambiente: {name}")
    return v

TELEGRAM_TOKEN = env("TELEGRAM_TOKEN", required=True)
CHAT_ID = env("CHAT_ID", required=True)
AFFILIATE_ID = env("AFFILIATE_ID", required=True)  # ex: dionatanrenzz
FEED_URL = env("FEED_URL", required=True)          # link do RSS gerado
INTERVAL_SECONDS = int(env("INTERVAL_SECONDS", "300"))

def log(msg):
    print(msg, flush=True)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    r = requests.post(url, data=payload, timeout=30)
    log(f"[telegram] status={r.status_code} resp={r.text[:200]}")
    r.raise_for_status()

def add_affiliate(link: str) -> str:
    """
    Adiciona matt_word=AFFILIATE_ID no link.
    Se já existir matt_word, substitui.
    """
    try:
        p = urlparse(link)
        q = dict(parse_qsl(p.query, keep_blank_values=True))
        q["matt_word"] = AFFILIATE_ID
        new_query = urlencode(q, doseq=True)
        return urlunparse((p.scheme, p.netloc, p.path, p.params, new_query, p.fragment))
    except Exception:
        # se der qualquer problema de parse, devolve o link original
        return link

def fetch_feed():
    # Alguns feeds bloqueiam user-agent "genérico"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; PromotopBot/1.0)"}
    r = requests.get(FEED_URL, headers=headers, timeout=30)
    log(f"[rss] status={r.status_code}")
    r.raise_for_status()
    feed = feedparser.parse(r.text)
    return feed.entries or []

def format_item(entry):
    title = (entry.get("title") or "").strip()
    link = (entry.get("link") or "").strip()
    if link:
        link = add_affiliate(link)

    # tenta pegar preço se o feed tiver (alguns geradores colocam em summary)
    summary = (entry.get("summary") or "").strip()

    msg = f"🔥 OFERTA NOVA\n\n📌 {title}\n\n🔗 {link}"
    if summary and summary.lower() not in title.lower():
        # evita mandar summary gigante
        s = summary.replace("\n", " ").strip()
        if len(s) > 180:
            s = s[:180] + "..."
        msg += f"\n\n📝 {s}"
    return msg

def entry_id(entry):
    # alguns feeds usam id/guid, outros usam link
    return (entry.get("id") or entry.get("guid") or entry.get("link") or entry.get("title") or "").strip()

def main():
    log("🤖 Bot RSS iniciado com sucesso")
    send_telegram("✅ Bot RSS online. Vou monitorar o feed e avisar quando surgir item novo.")

    seen = set()
    warmup = True

    while True:
        try:
            entries = fetch_feed()
            if not entries:
                log("Nenhum item no feed agora.")
            else:
                # processa do mais antigo pro mais novo
                new_count = 0
                for e in reversed(entries[:20]):  # limita pra não explodir
                    eid = entry_id(e)
                    if not eid:
                        continue
                    if eid in seen:
                        continue

                    seen.add(eid)
                    if warmup:
                        # na primeira rodada, só “aprende” os itens existentes
                        continue

                    msg = format_item(e)
                    send_telegram(msg)
                    new_count += 1

                log(f"Itens novos enviados: {new_count}")

            warmup = False
            log(f"⏳ Dormindo {INTERVAL_SECONDS}s...")
            time.sleep(INTERVAL_SECONDS)

        except Exception as ex:
            log(f"❌ ERRO: {ex}")
            time.sleep(30)

if __name__ == "__main__":
    main()
