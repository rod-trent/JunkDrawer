import os
import time
import requests
from cachetools import TTLCache
from dotenv import load_dotenv

load_dotenv()

HIBP_API_KEY = os.getenv("HIBP_API_KEY")
HEADERS = {
    "hibp-api-key": HIBP_API_KEY,
    "User-Agent": "BreachWise/1.0 (+https://github.com/yourname/breachwise)"
}

# Global cache + aggressive caching (7 days for emails, 1 hour for global breaches)
cache = TTLCache(maxsize=5000, ttl=604800)  # 7 days for email results

BASE_URL = "https://haveibeenpwned.com/api/v3"

# Single global rate-limiter (ensures only ONE request every 2 seconds)
_last_request_time = 0

def _rate_limit():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < 2.1:  # 2.1 seconds > HIBP’s 1500 ms rule
        time.sleep(2.1 - elapsed)
    _last_request_time = time.time()

def _get(url):
    _rate_limit()
    resp = requests.get(url, headers=HEADERS, timeout=10)
    return resp

def get_breaches_for_email(email: str):
    if email.lower() in cache:
        return cache[email.lower()]

    url = f"{BASE_URL}/breachedaccount/{email}?truncateResponse=false&includeUnverified=true"
    resp = _get(url)

    if resp.status_code == 200:
        result = resp.json()
    elif resp.status_code == 404:
        result = []
    elif resp.status_code == 429:
        retry_after = int(resp.headers.get("Retry-After", "2"))
        st.warning(f"HIBP rate limit hit. Waiting {retry_after} seconds...")
        time.sleep(retry_after + 1)
        return get_breaches_for_email(email)  # retry once
    else:
        raise Exception(f"HIBP Error {resp.status_code}: {resp.text}")

    cache[email.lower()] = result
    return result

def get_all_breaches():
    if "all_breaches" in cache:
        return cache["all_breaches"]

    url = f"{BASE_URL}/breaches"
    resp = _get(url)
    if resp.status_code == 200:
        result = resp.json()
        cache["all_breaches"] = result
        return result[-5:]  # latest 5
    return []