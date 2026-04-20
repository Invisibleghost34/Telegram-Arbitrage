import requests
from scipy.optimize import linprog
from database import init_db, insert_market, insert_snapshot, insert_trade


#Token ids
YES_TOKEN = "100379208559626151022751801118534484742123694725746262280150222742563282755057"
NO_TOKEN  = "113732820231608904682346496304917888352004831436510840986547065248348999143469"

#API 
BASE_URL = "https://clob.polymarket.com"
GAMMA_URL = "https://gamma-api.polymarket.com"

#Categories of Markets 
SLUGS = ["politics", "sports", "crypto", "economics"]

# portfolio = {
#     "cash": 1000.0,
#     "yes_shares": 0,
#     "no_shares": 0
# }
def get_markets():
    url = f"{GAMMA_URL}/markets"
    count = 0
    params = {
        "active": True,
        "closed": False,
        "limit": 500,
        "acceptingOrders": True
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    markets = response.json()
    print(f"Total markets fetched: {len(markets)}")
    for market in markets:
        events = market.get("events", [])
        if events:
            print(events[0].get("ticker"))
        count += 1 
        print(market["question"])
        print(market["clobTokenIds"])
        print(count)
    return markets

#TO-DO Fix the way token ids for yes and no are imported into the database 
#fix the arbitrage detection logic

def paper_trade(yes_price, no_price, shares):
    cost = (yes_price + no_price) * shares
    if portfolio["cash"] < cost:
        print("Not enough funds")
        return
    portfolio["cash"] -= cost 
    portfolio["yes_shares"] += shares 
    portfolio["no_shares"] += shares 
    print(f"PAPER BUY — {shares} YES at {yes_price} + {shares} NO at {no_price}")
    print(f"Cost: {cost:.2f} | Cash remaining: {portfolio['cash']:.2f}")

def calculate_shares(yes_price, no_price, portfolio):
    cash = portfolio["cash"]
    
    c = [0, 0, -1]
    
    A_ub = [
        [yes_price, no_price, 0],  # total spend <= cash
        [-1, 0, 1],                 # z <= yes_shares
        [0, -1, 1],                 # z <= no_shares
    ]
    b_ub = [cash, 0, 0]
    
    bounds = [(0, None), (0, None), (0, None)]
    
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
    
    if result.success:
        yes_shares = int(result.x[0])
        no_shares = int(result.x[1])
        cost = (yes_shares * yes_price) + (no_shares * no_price)
        profit_if_yes = yes_shares - cost
        profit_if_no = no_shares - cost
        print(f"Yes shares: {yes_shares}")
        print(f"No shares: {no_shares}")
        print(f"Total cost: {cost:.2f}")
        print(f"Profit if YES wins: {profit_if_yes:.2f}")
        print(f"Profit if NO wins: {profit_if_no:.2f}")
        return yes_shares, no_shares
    else:
        print("No optimal solution found")
        return 0, 0

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

   
       
    conn = init_db()
    markets = get_markets()

    for market in markets:
        insert_market(conn, market)
        tokens = market.get("clobTokenIds", [])
        if len(tokens) < 2: 
            continue 
        try: 
            yes_ob = get_orderbook(tokens[0])
            no_ob = get_orderbook(tokens[1])
            yes_ask = get_best_ask(yes_ob)
            no_ask = get_best_ask(no_ob)
            if yes_ask is None or no_ask is None: 
                continue 
            insert_snapshot(conn, market["id"], yes_ask, no_ask)
            total = yes_ask + no_ask 
            if total < 0.99:
                print(f"ARBITRAGE FOUND - {market['question']} | spread: {1 - total:.4f}" )
            else:
                 print(f"{market['question'][:50]} | total: {total:.4f}")
        except Exception as e:
            print(f"Error on {market['question'][:40]}: {e}")
            continue

    
    #testing the linear programming method 
    Yes = 0.34 
    No = 0.63 
    portfolio = {"cash": 10000}


    # last_yes = get_last_trade_price(yes_ob)
    # last_no = get_last_trade_price(no_ob)
    
    # yes_bid = get_best_bid(yes_ob)
    # no_bid = get_best_bid(no_ob)

    yes_price = get_best_ask(yes_ob)
    no_price  = get_best_ask(no_ob)

    yes_shares, no_shares = calculate_shares(Yes, No, portfolio)

    if yes_price is None or no_price is None:
        print("No asks available for one of the tokens.")
        return

    total = yes_price + no_price

    print(f"YES price (best ask): {yes_price}")
    print(f"NO price  (best ask): {no_price}")
    print(f"Sum YES + NO = {total}")
    

    if total != 1: 
        print("Arbitrage found")
        

if __name__ == "__main__":
    main()