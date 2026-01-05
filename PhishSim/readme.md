# Build Your Phishing Defense Skills with This AI-Powered Simulator

In an era where phishing attacks are more sophisticated than ever, staying ahead requires hands-on practice. As of January 2026, with cyber threats evolving alongside AI advancements, tools like **PhishSim** offer a timely solution. This open-source Streamlit app, powered by xAI's Grok models, simulates realistic phishing scenarios to train users in spotting malicious emails. Whether you're an individual sharpening your skills or a team enhancing security awareness, PhishSim turns learning into an engaging game.




### Why PhishSim Stands Out

Traditional phishing training often relies on static templates, but PhishSim leverages AI to generate dynamic, industry-specific messages—phishing or legitimate—tailored to sectors like Finance, Healthcare, Retail, Tech, or General. Difficulty levels (Easy, Medium, Hard) ensure progressive challenges.

Key features include:
- **AI-Driven Content**: Grok generates deceptive phishing emails with elements like urgency, fake links, or attachments, or professional legitimate ones.
- **Gamification**: Earn points, streaks, levels (Beginner to Master), and badges (e.g., "Streak Master" for 5 correct in a row, "Phishing Hunter" for 50 flagged phishing attempts).
- **Progress Tracking**: User profiles save scores, badges, industry stats, and leaderboards.
- **Real-Time Analyzer**: Paste any email for instant AI analysis.
- **Training Modules**: Quick guides on spotting phishing signs.

Unlike enterprise tools like Gophish for campaigns, PhishSim focuses on interactive, endless training for personal or small-group use.

### How It Works

1. Enter a username to track progress.
2. Generate a message and guess: Phishing or Legitimate?
3. Receive AI feedback, update your score/streak, and unlock badges.
4. Analyze real emails or view your profile/leaderboard.

### Requirements

To run PhishSim, you'll need:
- **Python 3.8+**: The app is built in Python.
- **Dependencies**: Install via `pip install streamlit requests python-dotenv pandas`.
  - Streamlit for the web interface.
  - Requests for API calls.
  - python-dotenv for loading environment variables.
  - Pandas for potential data handling (e.g., leaderboards).
- **xAI API Key**: Sign up at [x.ai](https://x.ai) and get an API key. Set it as `XAI_API_KEY` in a `.env` file.
- **Model Access**: The code defaults to "grok-3", but as of January 2026, xAI offers advanced models like "grok-4-fast-reasoning" with a 2,000,000 token context window for better reasoning and outputs. Update `MODEL_NAME` in the code to a current model (e.g., "grok-4-1-fast-reasoning") for optimal performance, especially if you have access to Grok-4 variants.
- **Optional**: For deployment, use Streamlit Community Cloud or a server.

No additional installations are needed beyond these, as the app uses built-in Python libraries for the rest.

### How to Implement

PhishSim's code is structured for simplicity and extensibility:

1. **Setup and Imports**: Loads libraries, environment variables, and defines the xAI API endpoint (`https://api.x.ai/v1/chat/completions`).
2. **Core Functions**:
   - `generate_message(is_phishing, industry, difficulty)`: Crafts prompts for Grok to create phishing or legit messages without revealing their nature.
   - `get_feedback(message, is_phishing, user_guess)`: Uses Grok to explain why the message is phishing/legit and provide spotting tips.
3. **User Management**: Handles logins, data persistence in JSON files (`user_data.json`, `leaderboard.json`), streaks, badges (defined in a dictionary), and levels based on scores.
4. **Streamlit Interface**: 
   - Sidebar for settings (industry, difficulty, navigation).
   - Main page for message generation, guessing, feedback, and real-time email analyzer.
   - Pages for training modules, leaderboard, and profile with badge displays.
5. **Badge System**: Comprehensive checks award badges like "First Win" or "Hard Mode Hero" after correct guesses.
6. **Error Handling**: Basic checks for API responses.

To customize:
- Add industries or difficulties by extending selectboxes.
- Enhance badges or integrate more AI features (e.g., image analysis for email screenshots).
- Update prompts for more deceptive phishing as Grok models evolve.

The app emphasizes ethical use—messages are for training only.

### How to Run It

1. **Clone the Repo**: `git clone https://github.com/rod-trent/JunkDrawer.git` (navigate to `/PhishSim`).
2. **Install Dependencies**: Run `pip install -r requirements.txt` (create one with the listed packages if needed).
3. **Set Environment**: Create `.env` with `XAI_API_KEY=your_key_here`.
4. **Update Model**: Change `MODEL_NAME` to a current one like "grok-4-fast-reasoning" for better results.
5. **Launch**: `streamlit run PhishSim.py`.
6. **Access**: Open in your browser (default: http://localhost:8501). Enter a username to start.

For production, deploy to Streamlit Cloud: Upload to GitHub, connect to Streamlit, and set secrets for the API key.

### Get Started Today

PhishSim empowers you to build real-world defenses against phishing. Fork it, contribute (e.g., more industries or multi-user support), or deploy for your team. Stay vigilant—train with AI to outsmart AI threats! 🔒🎣

*Disclaimer: For educational purposes only. Always comply with API terms and ethical guidelines.*
