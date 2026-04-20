import requests
import json

def get_pisa_ids():
    # 1. Query the specific market slug for Pisa
    slug = "will-pisa-be-relegated-from-serie-a-after-the-2025-26-season"
    url = f"https://gamma-api.polymarket.com/markets?slug={slug}"
    
    try:
        response = requests.get(url).json()
        if not response:
            return "Slug not found. Polymarket may have changed the URL name."

        market = response[0]
        raw_tokens = market.get("clobTokenIds")

        # FIX: Ensure we have a list, not a string
        if isinstance(raw_tokens, str):
            token_list = json.loads(raw_tokens)
        else:
            token_list = raw_tokens

        return {
            "yes": token_list[0],
            "no": token_list[1],
            "condition_id": market.get("conditionId")
        }
    except Exception as e:
        return f"Error: {e}"

# Usage
pisa_data = get_pisa_ids()
print(f"Pisa YES Token: {pisa_data['yes']}")
print(f"Pisa NO Token: {pisa_data['no']}")