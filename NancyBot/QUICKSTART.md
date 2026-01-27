# NancyBot Quick Start Guide

Get NancyBot up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - For making API calls
- `python-dotenv` - For loading environment variables

## Step 2: Set Up Your API Key

1. **Get your xAI API key**:
   - Go to [console.x.ai](https://console.x.ai)
   - Sign in or create an account
   - Navigate to API Keys
   - Create a new API key
   - Copy the key (starts with `xai-`)

2. **Create your `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Add your API key** to `.env`:
   ```
   XAI_API_KEY=xai-your_actual_key_here
   ```

## Step 3: Test Your Setup

**IMPORTANT**: Always test before running the full bot!

```bash
python test_xai_api.py
```

✅ **Success looks like**:
```
✓ API Key loaded: xai-...
Testing xAI API connection...
Status Code: 200
✅ SUCCESS! API is working correctly.
```

❌ **If you see errors**:
- 404 Error: Check your API key has Chat Completions enabled
- 401 Error: Your API key is invalid
- Timeout: Check your internet connection

## Step 4: Run NancyBot

```bash
python nancybot.py
```

You'll see:
```
🤖 NancyBot Starting...
Check interval: 1.0 hours
Press Ctrl+C to stop

[2026-01-27 15:30:00] Checking for new trades...
```

## What Happens Next?

NancyBot will:
1. Check for Nancy Pelosi's recent stock trades using xAI
2. Compare against previously seen trades
3. Alert you if new trades are found with AI analysis
4. Wait for the interval period (default: 1 hour)
5. Repeat

## Example Output

When a new trade is found:
```
🆕 New trade detected!

============================================================
🚨 NEW TRADE ALERT - Nancy Pelosi
============================================================

Date: 2026-01-15
Stock: NVDA - NVIDIA Corporation
Type: BUY
Amount: $1,000 - $15,000

AI Analysis:
NVIDIA Corporation is a leading technology company specializing in 
graphics processing units (GPUs) and AI computing. Recent developments 
include strong AI chip demand and data center growth. This trade timing 
coincides with the company's latest earnings announcement showing 
record revenue in AI segments.

============================================================

✅ Found 1 new trade(s)
```

## Customization Tips

### Change Check Frequency

Edit `nancybot.py` at the bottom:

```python
# Check every 30 minutes
bot.run(check_interval=1800)

# Check every 6 hours
bot.run(check_interval=21600)

# Check once daily at startup
bot.run(check_interval=86400)
```

### Run in Background

**Linux/Mac**:
```bash
nohup python nancybot.py > nancybot.log 2>&1 &
```

**Windows** (PowerShell):
```powershell
Start-Process python -ArgumentList "nancybot.py" -NoNewWindow -RedirectStandardOutput "nancybot.log"
```

## File Structure

After running, you'll have:
```
├── nancybot.py              # Main bot code
├── test_xai_api.py          # API test script
├── requirements.txt         # Dependencies
├── .env                     # Your API key (keep secret!)
├── .env.example             # Template for .env
├── trades_history.json      # Tracked trades (created automatically)
├── README.md                # Full documentation
├── TROUBLESHOOTING.md       # Detailed troubleshooting
└── QUICKSTART.md            # This file!
```

## Common Issues

### "XAI_API_KEY not found"
- Make sure `.env` file exists in the same directory
- Check the file contains: `XAI_API_KEY=xai-...`
- No quotes needed around the API key

### "404 Not Found"
- Verify your API key has Chat Completions access
- Check [console.x.ai](https://console.x.ai) permissions
- Try the test script first: `python test_xai_api.py`

### "No trades found"
- This is normal! Nancy Pelosi may not have recent trades
- The bot will keep checking on the schedule
- Try reducing the check interval for testing

### Bot stops unexpectedly
- Check you have a stable internet connection
- Verify your API key is still valid
- Look for error messages in the output
- Try increasing timeout in the code (already set to 1 hour)

## Next Steps

1. **Set up notifications** - Add email, Discord, or SMS alerts (see README.md)
2. **Run as a service** - Configure systemd or Windows Task Scheduler (see README.md)
3. **Track more politicians** - Extend the bot to monitor others (see README.md)
4. **Integrate real data sources** - Connect to Capitol Trades API (see README.md)

## Need Help?

- 📖 Check **README.md** for full documentation
- 🔧 See **TROUBLESHOOTING.md** for detailed error solutions
- 🌐 Visit [docs.x.ai](https://docs.x.ai) for xAI API documentation

---

**Happy Trading Monitoring! 📈🤖**
