import requests
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"


# -------------------------
# Fetch markets
# -------------------------
def fetch_markets():

    r = requests.get(
        f"{GAMMA_API}/markets",
        params={
            "limit": 1000,
            "active": True,
            "closed": False
        }
    )

    markets = r.json()

    # keep only 2 outcome markets
    filtered = []

    for m in markets:
        tokens = m.get("clobTokenIds")

        if not tokens:
            continue

        token_ids = ast.literal_eval(tokens)

        if len(token_ids) == 2:
            filtered.append((m["question"], token_ids))

    return filtered


# -------------------------
# Fetch orderbook best ask
# -------------------------
def get_best_ask(token_id):

    try:
        r = requests.get(
            f"{CLOB_API}/book",
            params={"token_id": token_id},
            timeout=3
        )

        book = r.json()
        asks = book.get("asks")

        if not asks:
            return None, 0

        price = float(asks[0]["price"])
        size = float(asks[0]["size"])

        return price, size

    except:
        return None, 0


# -------------------------
# Check single market
# -------------------------
def check_market(market):

    question, token_ids = market
    yes_token, no_token = token_ids

    yes_price, yes_size = get_best_ask(yes_token)
    no_price, no_size = get_best_ask(no_token)

    if yes_price is None or no_price is None:
        return None

    total = yes_price + no_price

    if total < 1:

        profit = 1 - total
        liquidity = min(yes_size, no_size)

        return {
            "question": question,
            "yes": yes_price,
            "no": no_price,
            "profit": profit,
            "liquidity": liquidity
        }

    return None


# -------------------------
# Main scanner
# -------------------------
def scan_arbitrage():

    markets = fetch_markets()

    print(f"Scanning {len(markets)} markets...\n")

    opportunities = []

    with ThreadPoolExecutor(max_workers=30) as executor:

        futures = [executor.submit(check_market, m) for m in markets]

        for future in as_completed(futures):

            result = future.result()

            if result:
                opportunities.append(result)

                print("ARBITRAGE FOUND")
                print(result["question"])
                print("YES:", result["yes"])
                print("NO :", result["no"])
                print("Profit:", round(result["profit"], 4))
                print("Liquidity:", result["liquidity"])
                print()


scan_arbitrage()