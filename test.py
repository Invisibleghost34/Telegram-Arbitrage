import requests

# Your token IDs
YES_TOKEN = "100379208559626151022751801118534484742123694725746262280150222742563282755057"
NO_TOKEN  = "113732820231608904682346496304917888352004831436510840986547065248348999143469"

BASE_URL = "https://clob.polymarket.com"

def get_orderbook(token_id):
    """Fetch the orderbook for a token."""
    url = f"{BASE_URL}/book?token_id={token_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_best_ask(orderbook):
    asks = orderbook.get("asks", [])
    if not asks:
        return None
    # Take the lowest ask
    return float(asks[-1]["price"])

def get_last_trade_price(orderbook):
    last_price = orderbook.get("last_trade_price")
    if not last_price:
        return None
    return float(last_price)

def get_best_bid(orderbook):
    bids = orderbook.get("bids", [])
    return float(bids[-1]["price"]) if bids else None

def main():
    yes_ob = get_orderbook(YES_TOKEN)
    no_ob  = get_orderbook(NO_TOKEN)
   

    # last_yes = get_last_trade_price(yes_ob)
    # last_no = get_last_trade_price(no_ob)
    
    # yes_bid = get_best_bid(yes_ob)
    # no_bid = get_best_bid(no_ob)

    yes_price = get_best_ask(yes_ob)
    no_price  = get_best_ask(no_ob)

    if yes_price is None or no_price is None:
        print("No asks available for one of the tokens.")
        return

    total = yes_price + no_price

    print(f"YES price (best ask): {yes_price}")
    print(f"NO price  (best ask): {no_price}")
    print(f"Sum YES + NO = {total}")

if __name__ == "__main__":
    main()