# Quick Start Guide

## Setup (5 minutes)

1. **Install Python dependencies:**
   ```bash
   cd garmin-chat-bot
   pip install -r requirements.txt
   ```

2. **Configure credentials:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your actual credentials:
   - Get xAI API key from: https://console.x.ai/
   - Use your Garmin Connect email and password

3. **Run the app:**
   ```bash
   python app.py
   ```

4. **Use the chatbot:**
   - Browser opens automatically at http://127.0.0.1:7860
   - Click "Connect to Garmin"
   - Start asking questions!

## Example Questions

Try these to get started:
- "How many steps did I take today?"
- "What was my last workout?"
- "How did I sleep last night?"
- "Show me my 5 most recent activities"
- "What's my calorie burn for today?"
- "Did I meet my step goal yesterday?"

## Key Features

- **Smart Context**: The bot automatically fetches relevant data based on your question
- **Follow-ups**: Ask related questions - it remembers the conversation
- **Refresh**: Click "Refresh Data" after syncing new activities
- **Reset**: Start fresh with "Reset Chat"

## Troubleshooting

**Can't authenticate with Garmin?**
- Double-check email/password in `.env`
- Try logging into Garmin Connect via web browser first

**xAI API errors?**
- Verify API key is correct
- Check you have credits available at console.x.ai

**No data showing?**
- Wait for devices to sync to Garmin Connect
- Click "Refresh Data" button
- Check that you have recent activities logged

That's it! Enjoy chatting with your fitness data. 🏃‍♂️
