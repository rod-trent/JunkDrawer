# **Build Your Phishing Defense Skills with This AI-Powered Simulator**

In today's digital world, **phishing attacks** remain one of the top cybersecurity threats, tricking even savvy users into revealing sensitive information. Traditional training often falls short against evolving tactics, but what if you could practice spotting them in a fun, gamified way?

Introducing **PhishSim**, an open-source, **AI-powered phishing simulator and trainer** built with Streamlit and powered by xAI's Grok models. This app generates realistic phishing or legitimate emails on demand, lets you guess if they're malicious, and provides detailed AI feedback to help you improve.

### **Why PhishSim Stands Out**

- **AI-Generated Realism**: Using xAI's Grok API, PhishSim creates deceptive phishing emails (with urgency, fake links, etc.) or benign ones tailored to industries like Finance, Healthcare, Retail, Tech, or General. Difficulty levels (Easy, Medium, Hard) ramp up the challenge.
- **Gamification for Engagement**: Track your score, streak, level (from Beginner to Master), and earn badges like "Phishing Hunter" (50 correct phishing flags), "Hard Mode Hero," or "Perfect Round." Daily logins reward consecutive day streaks.
- **Personalized Progress**: User profiles persist scores, badges, and industry-specific stats. A global leaderboard fosters competition.
- **Instant Real-Time Analyzer**: Paste any suspicious email for on-the-spot AI analysis and confidence scoring.
- **Basic Training Modules**: Quick tips on common phishing signs like urgency, mismatched links, or generic greetings.

Unlike traditional open-source tools like Gophish (focused on campaign management for organizations), PhishSim targets **individual or team training** with endless, varied AI-generated scenarios—no predefined templates needed.

### **How It Works**

1. Enter a username to track progress.
2. Generate a message and decide: Phishing or Legitimate?
3. Get immediate feedback, score updates, and expert tips from Grok.
4. Check your profile for badges, leaderboard for top scores, or analyze real emails.

The code uses xAI's chat completions endpoint with a recent Grok model (update from deprecated grok-beta). It requires an xAI API key (get one at https://x.ai/api) and runs locally or deployable via Streamlit sharing.

### **Get Started Today**

PhishSim is perfect for personal skill-building, team training, or cybersecurity enthusiasts. Hone your instincts against AI-crafted attacks that mimic real threats.

Source code and app: https://github.com/rod-trent/JunkDrawer/edit/main/PhishSim/

Deploy your own instance, contribute improvements, or fork it for custom features. Stay safe out there—train hard, phish smarter! 🔒🎣

*Note: Always practice ethical use. This tool is for education and awareness only.*
