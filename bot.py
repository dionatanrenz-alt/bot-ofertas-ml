import os
import time
import requests

# --------- ENV VARS (Render) ----------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
AFFILIATE_ID = os.getenv("AFFILIATE_ID", "promotop1")

ML_CLIENT_ID = os.getenv("ML_CLIENT_ID")
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")
ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI", "https://example.com")
ML_REFRESH_TOKEN = os.getenv("ML_REFRESH_TOKEN")

# --------- BASIC VALIDATION ----------
def require_env(name, value):
    if not value:
        raise RuntimeError(f"Falta variável de ambiente: {name}")

require_env("TELEGRAM_TOKEN", TELEGRAM_TOKEN)
require_env("CHAT_ID", CHAT_ID)
require_env("AFFILIATE_ID", AFFILIATE_ID)
require_env("ML_CLIENT_ID", ML_CLIENT_ID)
require_env("ML_CLIENT_SECRET", ML_CLIENT_SECRET)
require_env("ML_REFRESH_TOKEN", ML_REFRESH_TOKEN)

# --------- LOG ----------
def log(msg):
    print(msg, flush=True)

# --------- TELEGRAM ----------
def telegram_send(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    log(f"[telegram] status={r.status_code} resp={r.text[:200]}")
    return r.status_code == 200

# --------- ML TOKEN (refresh) ----------
_access_token = None
_access_token_exp = 0  # unix time

def ml_refresh_access_token():
    global _access_token, _access_token_exp, ML_REFRESH_TOKEN

    url = "https://api.mercadolibre.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "refresh_token": ML_REFRESH_TOKEN,
    }

    r = requests.post(url, data=data, timeout=30)
    log(f"[ml-token] status={r.status_code} resp={r.text[:200]}")

    r.raise_for_status()
    j = r.json()

    _access_token = j.get("access_token")
    expires_in = int(j.get("expires_in", 0))
    # renova um pouco antes de expirar
    _access_token_exp = int(time.time()) + max(expires_in - 60, 60)

    # às vezes o ML devolve refresh_token novo
    new_refresh = j.get("refresh_token")
    if new_refresh and new_refresh != ML_REFRESH_TOKEN:
        ML_REFRESH_TOKEN = new_refresh
        log("[ml-token] Refresh token foi atualizado (salve no Render se quiser).")

    return _access_token

def ml_get_access_token():
    global _access_token, _access_token_exp
    now = int(time.time())
    if (not _access_token) or (now >= _access_token_exp):
        return ml_refresh_access_token()
    return _access_token

# --------- ML SEARCH ----------
# Você pode trocar categoria e termo abaixo:
CATEGORY_ID = "MLB1055"   # Eletrônicos
QUERY = None             # ex: "iphone", ou deixe None

_last_sent_ids = set()

def buscar_oferta():
    token = ml_get_access_token()

    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {
        "category": CATEGORY_ID,
        "sort": "price_asc",
        "limit": 5
    }
    if QUERY:
        params["q"] = QUERY

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    r = requests.get(url, params=params, headers=headers, timeout=30)
    log(f"[ml] status={r.status_code}")
    if r.status_code != 200:
        log(f"[ml] resp={r.text[:200]}")
        return None

    data = r.json()
    results = data.get("results", [])
    if not results:
        return None

    # pega o primeiro item que ainda não foi enviado
    for p in results:
        pid = p.get("id")
        if not pid or pid in _last_sent_ids:
            continue

        title = p.get("title", "Sem título")
        price = p.get("price", "")
        permalink = p.get("permalink", "")

        # link afiliado (matt_word)
        if "?" in permalink:
            link = f"{permalink}&matt_word={AFFILIATE_ID}"
        else:
            link = f"{permalink}?matt_word={AFFILIATE_ID}"

        msg = (
            f"🔥 OFERTA MERCADO LIVRE\n\n"
            f"📌 {title}\n"
            f"💰 R$ {price}\n\n"
            f"👉 {link}"
        )

        _last_sent_ids.add(pid)
        # limita memória
        if len(_last_sent_ids) > 200:
            _last_sent_ids.clear()

        return msg

    return None

# --------- MAIN LOOP ----------
def main():
    telegram_send("✅ Bot iniciado e conectado. (teste)")

    while True:
        try:
            oferta = buscar_oferta()
            if oferta:
                telegram_send(oferta)
            else:
                log("Nenhuma oferta encontrada")
            log("⏳ Dormindo 300s...")
            time.sleep(300)  # 5 minutos
        except Exception as e:
            log(f"❌ ERRO no loop: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
