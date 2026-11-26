import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("CARTESIA_API_KEY")
headers = {
    "X-API-Key": api_key,
    "Cartesia-Version": "2025-04-16",
}

def fetch_voices(language=None, limit=100):
    params = {"limit": limit}
    if language:
        params["language"] = language
    resp = requests.get("https://api.cartesia.ai/voices", headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", data) if isinstance(data, dict) else data

sv_voices = fetch_voices(language="sv", limit=50)
print(f"--- Swedish-tagged voices ({len(sv_voices)}) ---")
for v in sv_voices:
    print(f"ID: {v['id']} | Lang: {v.get('language')} | Name: {v['name']}")

if not sv_voices:
    print("No 'sv'-tagged voices returned on page 1. Any Sonic-3 voice supports language='sv' cross-lingually.")