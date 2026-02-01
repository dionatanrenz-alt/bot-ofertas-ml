def buscar_oferta():
    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {
        "category": "MLB1055",  # Eletrônicos
        "sort": "price_asc",
        "limit": 1
    }

    resp = requests.get(url, params=params)
    log(f"ML status={resp.status_code}")

    data = resp.json()

    if "results" not in data or len(data["results"]) == 0:
        log("Nenhuma oferta encontrada")
        return None

    p = data["results"][0]

    link = f"{p['permalink']}?matt_word={AFFILIATE_ID}"

    msg = (
        "🔥 OFERTA MERCADO LIVRE 🔥\n\n"
        f"{p['title']}\n"
        f"💰 R$ {p['price']}\n\n"
        f"👉 {link}"
    )

    return msg
