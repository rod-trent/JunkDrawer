"""
NancyBot - Congressional Stock Trade Monitor
Tracks Nancy Pelosi's stock trades and notifies users of new activity
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv

class NancyBot:
    def __init__(self):
        load_dotenv()
        self.xai_api_key = os.getenv('XAI_API_KEY')
        # Correct xAI API endpoint
        self.xai_api_base = os.getenv('XAI_API_BASE', 'https://api.x.ai')
        
        if not self.xai_api_key:
            raise ValueError("XAI_API_KEY not found in .env file")
        
        self.trades_file = 'trades_history.json'
        self.known_trades = self.load_known_trades()
        
    def load_known_trades(self) -> set:
        """Load previously seen trades from file"""
        if os.path.exists(self.trades_file):
            with open(self.trades_file, 'r') as f:
                data = json.load(f)
                return set(data.get('trade_ids', []))
        return set()
    
    def save_known_trades(self):
        """Save known trades to file"""
        with open(self.trades_file, 'w') as f:
            json.dump({
                'trade_ids': list(self.known_trades),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def query_xai(self, prompt: str) -> str:
        """Query xAI API with a prompt"""
        headers = {
            'Authorization': f'Bearer {self.xai_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a financial analyst assistant that helps track congressional stock trades. Provide concise, factual information.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'model': 'grok-4',  # Correct model name per xAI docs
            'stream': False,
            'temperature': 0
        }
        
        try:
            response = requests.post(
                f'{self.xai_api_base}/v1/chat/completions',  # Correct endpoint path
                headers=headers,
                json=data,
                timeout=3600  # Longer timeout for reasoning models
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error querying xAI: {e}")
            if e.response:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error querying xAI: {e}")
            return None
    
    def fetch_pelosi_trades(self) -> List[Dict[str, Any]]:
        """
        Fetch Nancy Pelosi's stock trades from public sources
        Uses web search through xAI to find recent trades
        """
        
        # First, try to get recent trades via xAI with web search
        prompt = """
        Search the web for Nancy Pelosi's most recent stock trades disclosed in the last 30 days.
        Look for official House financial disclosures or Capitol Trades data.
        
        For each trade found, provide information in this EXACT format:
        
        TRADE 1:
        Date: YYYY-MM-DD
        Ticker: SYMBOL
        Type: BUY or SELL
        Amount: $X,XXX - $X,XXX
        Description: Company name and brief description
        
        TRADE 2:
        (repeat format)
        
        If no recent trades found, respond with: NO_TRADES_FOUND
        """
        
        response = self.query_xai(prompt)
        
        if not response:
            print("Failed to query xAI API")
            return []
        
        if "NO_TRADES_FOUND" in response:
            print("No recent trades found")
            return []
        
        # Parse the structured response
        trades = []
        trade_blocks = response.split('TRADE ')[1:]  # Split by TRADE marker
        
        for block in trade_blocks:
            try:
                trade = {}
                lines = block.strip().split('\n')
                
                for line in lines:
                    if line.startswith('Date:'):
                        trade['date'] = line.split('Date:')[1].strip()
                    elif line.startswith('Ticker:'):
                        trade['ticker'] = line.split('Ticker:')[1].strip()
                    elif line.startswith('Type:'):
                        trade['type'] = line.split('Type:')[1].strip()
                    elif line.startswith('Amount:'):
                        trade['amount'] = line.split('Amount:')[1].strip()
                    elif line.startswith('Description:'):
                        trade['description'] = line.split('Description:')[1].strip()
                
                # Only add if we have minimum required fields
                if trade.get('date') and trade.get('ticker'):
                    trades.append(trade)
                    
            except Exception as e:
                print(f"Error parsing trade block: {e}")
                continue
        
        return trades
    
    def generate_trade_id(self, trade: Dict[str, Any]) -> str:
        """Generate unique ID for a trade"""
        return f"{trade.get('date', '')}_{trade.get('ticker', '')}_{trade.get('type', '')}_{trade.get('amount', '')}"
    
    def analyze_trade(self, trade: Dict[str, Any]) -> str:
        """Use xAI to analyze the significance of a trade"""
        prompt = f"""
        Analyze this stock trade by Nancy Pelosi:
        
        Date: {trade.get('date')}
        Stock: {trade.get('ticker')} - {trade.get('description')}
        Type: {trade.get('type')}
        Amount: {trade.get('amount')}
        
        Provide a brief analysis covering:
        1. What this company does
        2. Recent news or developments
        3. Potential significance of this trade timing
        
        Keep it concise (3-4 sentences).
        """
        
        return self.query_xai(prompt)
    
    def notify_new_trade(self, trade: Dict[str, Any], analysis: str):
        """Notify user of new trade"""
        notification = f"""
{'='*60}
🚨 NEW TRADE ALERT - Nancy Pelosi
{'='*60}

Date: {trade.get('date')}
Stock: {trade.get('ticker')} - {trade.get('description')}
Type: {trade.get('type', '').upper()}
Amount: {trade.get('amount')}

AI Analysis:
{analysis}

{'='*60}
        """
        print(notification)
        
        # You could extend this to:
        # - Send email notifications
        # - Post to Discord/Slack
        # - Send SMS via Twilio
        # - Desktop notifications
    
    def check_for_new_trades(self):
        """Check for new trades and notify if found"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for new trades...")
        
        trades = self.fetch_pelosi_trades()
        
        if not trades:
            print("No trades found or unable to fetch data.")
            return
        
        new_trades_found = 0
        
        for trade in trades:
            trade_id = self.generate_trade_id(trade)
            
            if trade_id not in self.known_trades:
                # New trade detected!
                print(f"\n🆕 New trade detected!")
                analysis = self.analyze_trade(trade)
                self.notify_new_trade(trade, analysis)
                
                self.known_trades.add(trade_id)
                new_trades_found += 1
        
        if new_trades_found > 0:
            self.save_known_trades()
            print(f"\n✅ Found {new_trades_found} new trade(s)")
        else:
            print("No new trades since last check.")
    
    def run(self, check_interval: int = 3600):
        """
        Run the bot continuously
        
        Args:
            check_interval: Seconds between checks (default: 1 hour)
        """
        print("🤖 NancyBot Starting...")
        print(f"Check interval: {check_interval} seconds ({check_interval/3600:.1f} hours)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.check_for_new_trades()
                print(f"\n💤 Sleeping for {check_interval/3600:.1f} hours...")
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\n\n👋 NancyBot stopped by user")
            self.save_known_trades()

def main():
    try:
        bot = NancyBot()
        
        # Run with 1 hour intervals (adjust as needed)
        # For testing, you might want to use 300 (5 minutes)
        bot.run(check_interval=3600)
        
    except Exception as e:
        print(f"❌ Error starting NancyBot: {e}")

if __name__ == "__main__":
    main()
