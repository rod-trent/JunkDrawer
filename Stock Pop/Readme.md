# Introducing Stock Pop: Real-Time Stock Alerts Powered by Grok AI

In today's volatile stock market, keeping track of price movements can be a full-time job. That's where **Stock Pop**, a clever Python-based application, comes in. Developed as a handy utility, Stock Pop monitors your chosen stock tickers in the background and pops up notifications when there's a significant price swing. But what sets it apart is its integration with Grok AI from xAI, which provides instant trading recommendations to help you decide your next move. Let's dive into what this app is all about, why it's valuable, and how you can get it up and running on your Windows machine.

## What Is Stock Pop?

Stock Pop is a minimalist desktop app designed to run quietly in the Windows system tray. It uses the yfinance library to fetch real-time stock prices every minute and compares them against a user-set threshold (default 2%). If a stock's price changes by that amount or more, you'll get a desktop notification via the plyer library. The notification includes not just the price change details but also a concise trading signal from Grok AI—options like "Strong Buy," "Buy," "Hold," "Sell," or "Strong Sell," followed by a one-sentence explanation.

The app is built with a simple configuration window using Tkinter, where you can add up to five tickers and adjust the alert threshold. It stores your settings in a JSON file for persistence. Under the hood, it leverages the OpenAI client to query Grok (model: grok-4) for recommendations, making it a blend of traditional stock monitoring and cutting-edge AI insights.

The code is open-source and available in a GitHub repository, making it easy to tweak or expand.

## Why Is Stock Pop Valuable?

Stock trading isn't just about buying low and selling high—it's about timing and information. Stock Pop delivers value in several ways:

- **Real-Time Alerts**: No more glued to your screen or refreshing apps. Get notified instantly on price pops, allowing you to react quickly in a market where minutes matter.
  
- **AI-Powered Insights**: Grok's recommendations add an elite quantitative trading perspective. For example, if a stock surges 3%, Grok might signal "Strong Buy → Momentum breakout with volume surge, likely continues." This isn't financial advice, but it's a smart, brutally honest second opinion based on current data.

- **Customizability and Simplicity**: Monitor only the stocks you care about, with adjustable sensitivity. It's lightweight, daemon-like, and doesn't bog down your system.

- **Educational Tool**: For developers or trading enthusiasts, it's a great example of combining APIs (yFinance, xAI) with desktop features like notifications and tray icons.

In an era where AI is transforming finance, tools like Stock Pop democratize access to advanced insights without needing expensive subscriptions or complex setups.

## The Importance of Windows System Tray Integration

One of the standout features of Stock Pop is how it interacts with the Windows system tray (also known as the notification area). Many apps overwhelm users with always-on windows, but Stock Pop exemplifies best practices for background utilities:

- **Minimized Footprint**: By using the pystray library, the app creates a custom icon in the tray. This allows it to run persistently without cluttering your taskbar or desktop.

- **User-Friendly Access**: Right-click the icon to open the configuration menu or quit the app. This design is crucial for "set it and forget it" tools, ensuring they don't interrupt your workflow until necessary.

- **Background Processing**: The app uses threading to check stock prices every 60 seconds without freezing the UI. This demonstrates how to build efficient, non-blocking applications that handle periodic tasks.

Learning to work with the system tray is important for Windows developers because it enhances user experience for monitoring apps, like antivirus software, chat clients, or in this case, stock watchers. It shows how Python can create professional-grade desktop tools with minimal code.

![Stock Pop System Tray Icon](https://raw.githubusercontent.com/rod-trent/JunkDrawer/main/Stock%20Pop/SystemTray.jpg)

## Prerequisites

Before diving in, ensure you have the following:

- **Operating System**: Windows (required for system tray and native notifications).
- **Python**: Version 3.12 or later (the code uses Python 3 features).
- **API Key**: An xAI API key. Sign up at [x.ai](https://x.ai), then add it to a `.env` file as `XAI_API_KEY=your_key_here`.
- **Libraries**: Install via pip:
  - `yfinance` for stock data.
  - `python-dotenv` for loading environment variables.
  - `openai` for the xAI API client.
  - `pillow` (PIL) for generating the tray icon image.
  - `pystray` for system tray functionality.
  - `plyer` for cross-platform notifications.
  - `tkinter` (usually bundled with Python, but ensure it's available).
  -  `windows-toasts`
  -  `pystray`

You can install them all with:  
```
pip install yfinance python-dotenv openai pillow pystray plyer
```

## How to Implement Stock Pop

Implementing Stock Pop is straightforward since the code is ready-to-run. Here's a step-by-step guide:

1. **Download the Code**: Head to the GitHub repository at [https://github.com/rod-trent/JunkDrawer/tree/main/Stock%20Pop](https://github.com/rod-trent/JunkDrawer/tree/main/Stock%20Pop) and download `StockPop.py`. If there are additional files (like images), grab those too.

2. **Set Up Environment**: Create a `.env` file in the same directory as the script and add your xAI API key.

3. **Install Dependencies**: Run the pip command mentioned in prerequisites.

4. **Customize if Needed**: The code is well-commented. You could adjust the check interval (currently 60 seconds), add more features like logging, or modify the Grok prompt for different analysis styles.

5. **Run the App**: Execute `python StockPop.py` from the command line. It will load any existing config, start monitoring if tickers are set, and minimize to the tray.

If the API key is missing, it'll show an error message via Tkinter.

## How to Use Stock Pop

Using the app is intuitive:

1. **Launch and Tray**: Run the script—it goes straight to the system tray with a custom "POP" icon.

2. **Configure**: Right-click the tray icon and select "Configure." This opens the settings window.

   ![Stock Pop Configuration Window](https://github.com/rod-trent/JunkDrawer/blob/main/Stock%20Pop/stockpopnew.jpg)

3. **Set Options**:
   - **Alert Threshold**: Use the spinbox to set the percentage change (e.g., 2.0% for ±2%).
   - **Stocks to Monitor**: Enter tickers (e.g., AAPL, TSLA) one per line in the text box, up to 5.

4. **Save and Close**: Hit the button or press Enter. The app saves your config to `stock_config.json` and starts (or restarts) monitoring.

5. **Receive Alerts**: When a stock pops, you'll see a notification with the change, old/new prices, and Grok's recommendation. Notifications timeout after 25 seconds.

6. **Quit**: Right-click the tray icon and select "Quit."

If no tickers are set, it won't monitor anything, but you can always reopen config to add them.

## Final Thoughts

Stock Pop is a fantastic example of how Python can bridge finance, AI, and desktop usability. Whether you're a trader looking for an edge or a developer interested in system tray apps, it's worth trying. Remember, while Grok's recommendations are insightful, always do your own research— this is for informational purposes only.

If you build on it or have feedback, check out the repo and contribute! Happy trading!
