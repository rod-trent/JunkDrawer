# NancyBot 🤖

An intelligent agent that monitors Nancy Pelosi's stock trades using the xAI API and notifies you when new trades are disclosed.

## Features

- 🔍 **Automated Monitoring**: Continuously checks for new stock trades
- 🤖 **AI-Powered Analysis**: Uses xAI (Grok-4) to analyze trade significance
- 📊 **Trade Tracking**: Maintains history to avoid duplicate notifications
- 🔔 **Real-time Alerts**: Notifies you immediately when new trades are detected
- 💾 **Persistent Storage**: Remembers previously seen trades across restarts

## Prerequisites

- Python 3.8 or higher
- xAI API key (from [console.x.ai](https://console.x.ai))
- Ensure your API key has access to Chat Completions endpoint

## Installation

1. **Clone or download** the NancyBot files

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key**:
   - Copy `.env.example` to `.env`
   - Add your xAI API key:
     ```
     XAI_API_KEY=xai-your_actual_api_key_here
     ```

4. **Test your setup** (IMPORTANT - Do this first!):
   ```bash
   python test_xai_api.py
   ```
   
   You should see:
   ```
   ✓ API Key loaded: xai-...
   Testing xAI API connection...
   Status Code: 200
   ✅ SUCCESS! API is working correctly.
   ```

## Usage

### Basic Usage

Run the bot with default settings (checks every hour):

```bash
python nancybot.py
```

### Customizing Check Interval

Edit the `main()` function in `nancybot.py`:

```python
# Check every 5 minutes (for testing)
bot.run(check_interval=300)

# Check every 6 hours
bot.run(check_interval=21600)

# Check daily
bot.run(check_interval=86400)
```

### Running as a Background Service

**On Windows** (using Task Scheduler):
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., "At startup")
4. Action: Start a program → `python` with argument `C:\path\to\nancybot.py`

**On Linux/Mac** (using systemd or cron):

Create a systemd service file:
```bash
sudo nano /etc/systemd/system/nancybot.service
```

Add:
```ini
[Unit]
Description=NancyBot Stock Trade Monitor
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/nancybot
ExecStart=/usr/bin/python3 /path/to/nancybot/nancybot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nancybot
sudo systemctl start nancybot
sudo systemctl status nancybot
```

## How It Works

1. **Data Collection**: The bot uses xAI's Grok-4 model to search for Nancy Pelosi's recent stock trades
2. **Change Detection**: Compares against known trades stored in `trades_history.json`
3. **AI Analysis**: New trades are analyzed by xAI for context and significance
4. **Notification**: Alerts you with trade details and AI-generated insights
5. **Persistence**: Saves trade history to avoid duplicate notifications

## API Configuration

NancyBot uses the xAI Chat Completions API:
- **Endpoint**: `https://api.x.ai/v1/chat/completions`
- **Model**: `grok-4`
- **Authentication**: Bearer token (your API key)

Get your API key from the [xAI Console](https://console.x.ai/api-keys).

## Testing Your Setup

Before running NancyBot, test your API connection:

```bash
python test_xai_api.py
```

This verifies:
- ✓ API key is properly loaded from `.env`
- ✓ Connection to xAI API works
- ✓ Model name is correct
- ✓ You can receive responses

Expected output:
```
✓ API Key loaded: xai-...
Testing xAI API connection...
Endpoint: https://api.x.ai/v1/chat/completions
Model: grok-4

Status Code: 200
✅ SUCCESS! API is working correctly.

Response:
Hello from NancyBot test!

✓ NancyBot should work correctly now!
```

## Data Sources

Currently, the bot uses xAI to search for trade information. For production use, you should integrate with official data sources:

- **Capitol Trades API**: https://www.capitoltrades.com/
- **House Financial Disclosure**: https://disclosures-clerk.house.gov/
- **Senate Financial Disclosure**: https://efdsearch.senate.gov/

### Integrating a Real Data Source

Replace the `fetch_pelosi_trades()` method with an API call:

```python
def fetch_pelosi_trades(self) -> List[Dict[str, Any]]:
    # Example with Capitol Trades API
    response = requests.get(
        'https://api.capitoltrades.com/trades',
        params={'politician': 'nancy-pelosi'},
        headers={'Authorization': f'Bearer {self.capitol_trades_api_key}'}
    )
    return response.json()
```

## Extending Notifications

The bot currently prints to console. You can extend it to:

### Email Notifications
```python
import smtplib
from email.mime.text import MIMEText

def send_email_notification(self, trade, analysis):
    msg = MIMEText(f"New trade: {trade}\n\n{analysis}")
    msg['Subject'] = f"🚨 New Pelosi Trade: {trade.get('ticker')}"
    msg['From'] = 'nancybot@yourdomain.com'
    msg['To'] = 'your@email.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your@email.com', 'your_app_password')
        server.send_message(msg)
```

### Discord Webhook
```python
def send_discord_notification(self, trade, analysis):
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    data = {
        'content': f"🚨 **New Pelosi Trade**\n\n{trade}\n\n{analysis}"
    }
    requests.post(webhook_url, json=data)
```

### Desktop Notifications
```python
from plyer import notification

def send_desktop_notification(self, trade, analysis):
    notification.notify(
        title=f"New Pelosi Trade: {trade.get('ticker')}",
        message=f"{trade.get('type')} - {trade.get('amount')}",
        app_icon=None,
        timeout=10
    )
```

## Configuration Options

Edit these in the `NancyBot` class:

- `check_interval`: How often to check (in seconds)
- `xai_api_base`: xAI API endpoint (default: https://api.x.ai/v1)
- `trades_file`: Where to store trade history (default: trades_history.json)

## Files Generated

- `trades_history.json`: Stores known trades to prevent duplicate notifications

## Troubleshooting

**"XAI_API_KEY not found"**
- Ensure you've created a `.env` file with your API key

**No trades detected**
- The bot relies on xAI's knowledge, which may have limitations
- Consider integrating a dedicated financial disclosure API

**API rate limits**
- Adjust `check_interval` to check less frequently
- Consider caching xAI responses

## Legal & Ethical Considerations

This bot tracks **publicly disclosed** information that members of Congress are required to report. All trades are public record under the STOCK Act.

## Contributing

Feel free to enhance NancyBot with:
- Better data sources
- Additional notification methods
- Multi-politician tracking
- Historical analysis features
- Web dashboard interface

## License

MIT License - feel free to use and modify

## Disclaimer

This tool is for informational purposes only. Not financial advice. Always do your own research before making investment decisions.

---

Built with ❤️ and xAI
