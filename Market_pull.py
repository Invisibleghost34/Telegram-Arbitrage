import requests
import time
import json
from pprint import pprint

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, MarketOrderArgs, OrderType, OpenOrderParams, BalanceAllowanceParams, AssetType
from py_clob_client.order_builder.constants import BUY, SELL

GAMMA_API = "https://gamma-api.polymarket.com"
DATA_API = "https://data-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"




# Fetch active markets sorted by volume
response = requests.get(
    f"{GAMMA_API}/markets",
    params={
        "limit": 100,
        "active": True,
        "closed": False,
        "order": "volume24hr",
        "ascending": False
    }
)
markets = response.json()
print(f"Found {len(markets)} markets\n")



for m in markets[:50]:
    print(f"Question: {m['question']}")
    print(f"  Volume 24h: ${m.get('volume24hr', 0):,.0f}")
    print(f"  Liquidity: ${m.get('liquidityNum', 0):,.0f}")
    print(f"  Prices: {m.get('outcomePrices', 'N/A')}")
    print()
