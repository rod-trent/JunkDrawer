# 🏃‍♂️ Garmin Chat Bot

A local GenAI chatbot that connects to your Garmin Connect account, allowing you to ask natural language questions about your fitness data using xAI's API.

## Features

-   🔐 Secure local authentication with Garmin Connect
-   💬 Natural language interface powered by xAI (Grok)
-   📊 Query your fitness data: activities, steps, sleep, heart rate, and more
-   🎯 Context-aware responses based on your actual Garmin data
-   🔄 Real-time data refresh
-   💾 Conversation history for follow-up questions

## Prerequisites

-   Python 3.8 or higher
-   A Garmin Connect account
-   An xAI API key ([Get one here](https://console.x.ai/))

## Installation

1.  **Clone or download this repository**
2.  **Install dependencies:**

```bash
pip install -r requirements.txt
```

1.  **Set up your environment variables:**

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
XAI_API_KEY=your_xai_api_key_here
GARMIN_EMAIL=your_garmin_email@example.com
GARMIN_PASSWORD=your_garmin_password_here
```

## Usage

1.  **Start the application:**

```bash
python GarminChat.py
```

1.  **The Gradio interface will open in your browser automatically** (usually at `http://127.0.0.1:7860`)
2.  **Click "Connect to Garmin"** to authenticate with your Garmin Connect account
3.  **Start chatting!** Ask questions about your fitness data:
    1.  "How many steps did I take today?"
    2.  "What was my last workout?"
    3.  "How did I sleep last night?"
    4.  "Show me my recent activities"
    5.  "What are my calorie statistics?"

## Project Structure

```
garmin-chat-bot/
├── GarminChat.py          # Main Gradio application
├── garmin_handler.py      # Garmin Connect API wrapper
├── xai_client.py          # xAI API client
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## How It Works

1.  **Authentication**: The app authenticates with Garmin Connect using the `garminconnect` library
2.  **Data Retrieval**: Based on your question, it fetches relevant data (activities, sleep, steps, etc.)
3.  **Context Building**: Your Garmin data is formatted into a context string
4.  **AI Processing**: The question and context are sent to xAI's API (using Grok model)
5.  **Response**: The AI analyzes your data and provides a natural language answer

## Features by Component

### Garmin Handler (`garmin_handler.py`)

-   Authentication with Garmin Connect
-   Retrieval of activities, steps, heart rate, sleep, and body composition data
-   Smart data formatting for LLM context

### xAI Client (`xai_client.py`)

-   OpenAI-compatible interface to xAI API
-   Conversation history management
-   Token-efficient context handling
-   Uses `grok-3` model by default

### Gradio Interface (`GarminChat.py`)

-   Clean chat interface with examples
-   Connection status indicators
-   Data refresh capability
-   Conversation reset functionality

## Supported Data Types

The bot can answer questions about:

-   **Activities**: Recent workouts, runs, walks, bike rides, etc.
-   **Steps**: Daily step count and goals
-   **Calories**: Active and total calories burned
-   **Sleep**: Sleep duration, quality, deep/light/REM stages
-   **Heart Rate**: Heart rate data and trends
-   **Body Composition**: Weight and body composition metrics (if tracked)

## Tips for Best Results

1.  **Be specific**: "What was my longest run this week?" works better than "Tell me about running"
2.  **Ask follow-ups**: The bot maintains conversation context, so you can ask related questions
3.  **Refresh data**: Click "Refresh Data" if you just synced new activities to Garmin
4.  **Reset if needed**: Use "Reset Chat" to start a fresh conversation

## Troubleshooting

### Authentication Issues

-   Verify your Garmin email and password in `.env`
-   Make sure you can log in to Garmin Connect via web browser
-   Try refreshing data after initial connection

### API Errors

-   Check that your xAI API key is valid and has credits
-   Ensure you're using a supported model (default: `grok-2-1212`)
-   Check your internet connection

### Missing Data

-   Some Garmin data types require specific devices (e.g., body composition needs a compatible scale)
-   Recent activities may take time to sync from your device
-   Use the "Refresh Data" button after syncing

### Rate Limiting

-   Garmin Connect has unofficial API rate limits
-   The app caches data to minimize API calls
-   Wait a few minutes between data refreshes if you encounter issues

## Privacy & Security

-   All data stays local - the app runs entirely on your machine
-   Your Garmin credentials are stored only in your local `.env` file
-   Only the data needed to answer your question is sent to xAI's API
-   Conversation history is kept in memory and cleared when you close the app

## Model Customization

To use a different xAI model, edit `xai_client.py` and change the default model:

```python
def __init__(self, api_key: str, model: str = "grok-3"):
```

Available models (as of latest update):

-   `grok-3` (recommended, default)
-   `grok-vision-beta` (for vision tasks)

## Future Enhancements

Potential improvements you could add:

-   [ ] Export conversation to markdown/PDF
-   [ ] Visualizations and charts of fitness data
-   [ ] Goal tracking and recommendations
-   [ ] Multi-day trend analysis
-   [ ] Integration with other fitness platforms
-   [ ] Voice input/output support

## Credits

Built with:

-   [Gradio](https://gradio.app/) - Web UI framework
-   [garminconnect](https://github.com/cyberjunky/python-garminconnect) - Garmin Connect API wrapper
-   [xAI API](https://x.ai/) - AI model provider
-   [OpenAI Python SDK](https://github.com/openai/openai-python) - API client

## License

This is a personal project. Use at your own discretion and responsibility.

## Contributing

Feel free to fork and modify for your own use. This is a starting point for building your own Garmin data chatbot!

**Enjoy exploring your fitness data with AI! 🏃‍♂️💪**
