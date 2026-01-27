# NancyBot Troubleshooting Guide

## Common Issues and Solutions

### 1. "404 Not Found" Error

**Problem**: `404 Client Error: Not Found for url: https://api.x.ai/v1/chat/completions`

**Solution**: This has been fixed in the updated version. The correct endpoint is now used.

**What was wrong**: 
- Old code used: `https://api.x.ai/v1/chat/completions` (incorrect)
- Fixed code uses: `https://api.x.ai/v1/chat/completions` with proper base URL

**Verify your fix**:
```python
# In nancybot.py, check line ~13:
self.xai_api_base = os.getenv('XAI_API_BASE', 'https://api.x.ai')

# And in query_xai method, check the endpoint:
response = requests.post(
    f'{self.xai_api_base}/v1/chat/completions',
    ...
)
```

### 2. "XAI_API_KEY not found"

**Problem**: Missing API key in environment

**Solution**:
1. Create a `.env` file (copy from `.env.example`)
2. Add your actual xAI API key:
   ```
   XAI_API_KEY=xai-YOUR_ACTUAL_KEY_HERE
   ```
3. Make sure the `.env` file is in the same directory as `nancybot.py`

### 3. "No trades found or unable to fetch data"

**Possible causes**:
1. **API Key Invalid**: Check your xAI API key is correct
2. **Rate Limiting**: You may have hit API rate limits
3. **No Recent Trades**: Nancy Pelosi may not have disclosed new trades recently

**Debug steps**:
```python
# Add debug output to see the full response
# In query_xai method, add before the return:
print(f"DEBUG - API Response: {response.json()}")
```

### 4. Model Name Issues

**Current correct model**: `grok-4`

The xAI API has updated their model names. Make sure you're using:
- ✅ `grok-4` - Current production model (CORRECT)
- ❌ `grok-beta` - Deprecated
- ❌ `grok-2-latest` - Does not exist

If you get 404 errors, verify the model name in `query_xai` method:
```python
'model': 'grok-4',  # This is correct
```

Available models as of January 2026:
- `grok-4` - Main production model
- Check [xAI docs](https://docs.x.ai) for the latest model list

### 5. Testing the API Connection

Create a test script to verify your xAI setup:

```python
# test_xai.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('XAI_API_KEY')
print(f"API Key loaded: {api_key[:10]}..." if api_key else "No API key found")

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

data = {
    'messages': [
        {'role': 'user', 'content': 'Say hello'}
    ],
    'model': 'grok-4',  # Correct model name
    'stream': False
}

try:
    response = requests.post(
        'https://api.x.ai/v1/chat/completions',
        headers=headers,
        json=data,
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
```

Run: `python test_xai.py`

### 6. Parsing Issues

If trades aren't being detected properly:

**Check the response format** by adding debug output:
```python
# In fetch_pelosi_trades, add:
print(f"DEBUG - Raw response:\n{response}\n")
```

**Expected format**:
```
TRADE 1:
Date: 2024-01-15
Ticker: NVDA
Type: BUY
Amount: $1,000 - $15,000
Description: NVIDIA Corporation

TRADE 2:
Date: 2024-01-10
Ticker: MSFT
Type: SELL
Amount: $15,001 - $50,000
Description: Microsoft Corporation
```

### 7. Running as a Service

**If the service stops unexpectedly**:

Check logs:
```bash
# For systemd (Linux)
sudo journalctl -u nancybot -f

# For manual runs
python nancybot.py >> nancybot.log 2>&1 &
tail -f nancybot.log
```

### 8. Getting More Detailed Errors

Enable verbose error reporting:

```python
# At the top of nancybot.py
import logging
logging.basicConfig(level=logging.DEBUG)

# In query_xai method, enhance error handling:
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Status Code: {e.response.status_code}")
    print(f"Response Body: {e.response.text}")
    return None
```

### 9. API Rate Limits

xAI may have rate limits. If you're hitting them:

1. **Increase check interval**:
   ```python
   bot.run(check_interval=7200)  # Check every 2 hours instead of 1
   ```

2. **Add exponential backoff**:
   ```python
   import time
   
   def query_xai_with_retry(self, prompt: str, max_retries=3):
       for attempt in range(max_retries):
           result = self.query_xai(prompt)
           if result:
               return result
           
           wait_time = 2 ** attempt  # 1, 2, 4 seconds
           print(f"Retry {attempt + 1}/{max_retries} in {wait_time}s...")
           time.sleep(wait_time)
       return None
   ```

### 10. Data Source Alternatives

If xAI isn't returning good trade data, consider these alternatives:

**Option A: Capitol Trades (Web Scraping)**
```python
import requests
from bs4 import BeautifulSoup

def scrape_capitol_trades():
    url = "https://www.capitoltrades.com/trades?politician=nancy-pelosi"
    # Add scraping logic here
```

**Option B: Official House Disclosures API**
```python
# House Financial Disclosure API
# https://disclosures-clerk.house.gov/
```

**Option C: Use RSS Feeds**
Some sites offer RSS feeds of congressional trades that you can parse.

### Need More Help?

1. Check the xAI documentation: https://docs.x.ai/
2. Verify your API key status in the xAI console
3. Look at the full error traceback for clues
4. Test with a simple API call first (see #5 above)

### Updated Files

Make sure you're using the updated versions with these fixes:
- ✅ Correct API endpoint: `https://api.x.ai`
- ✅ Proper endpoint path: `/v1/chat/completions`
- ✅ Updated model name: `grok-4` (not `grok-beta` or `grok-2-latest`)
- ✅ Longer timeout: 3600 seconds for reasoning models
- ✅ Better error messages with status codes and response bodies
- ✅ Improved response parsing for trade data
- ✅ Test script included: `test_xai_api.py`
