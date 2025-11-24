import os
from xai_sdk import Client
from xai_sdk.chat import user, system
from dotenv import load_dotenv

load_dotenv()

# Initialize client with error check
GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    raise ValueError("GROK_API_KEY not found in .env file. Please add it.")

client = Client(
    api_key=GROK_API_KEY,
    timeout=3600  # Longer timeout for better reasoning
)

def analyze_with_grok(breaches, email="this user"):
    if not breaches:
        return "🎉 **No breaches found!** Your email has never appeared in any known data breach. You're doing great – keep using unique passwords and 2FA to stay safe. 🚀"

    # Build breach summary for prompt
    breach_text = "\n".join([
        f"- **{b['Name']}** ({b['BreachDate'][:4]}): Exposed {', '.join(b.get('DataClasses', []))}. Description: {b.get('Description', 'N/A')[:200]}..."
        for b in breaches
    ])

    prompt = f"""
You are a world-class cybersecurity expert speaking directly to a non-technical person like {email}.

Found in {len(breaches)} data breach(es):

{breach_text}

For each breach, give:
• **Risk level**: Low / Medium / High / Critical (based on data exposed and recency)
• **One-sentence plain-English explanation** of what happened and why it matters
• **Top 3 actions** (with priority: 🔥 High, ⚡ Medium, 📝 Low)

Then at the end:
• **Overall risk score**: 0–100 (0 = no worry, 100 = change everything now)
• **One short, honest personal summary** (kind but direct – e.g., "You're at moderate risk due to old password exposures")
• **One motivational closing line** to encourage better habits

Use emojis sparingly, short paragraphs, and be empathetic/human. Format with bold headers for readability.
"""

    # Model fallback chain (post-deprecation safe)
    models_to_try = ["grok-3", "grok-4", "grok-3-mini"]  # grok-3 is the official replacement for grok-beta

    for model in models_to_try:
        try:
            # Official xAI SDK chat builder pattern
            chat = client.chat.create(model=model)
            chat.append(system("You are Grok, a helpful cybersecurity advisor. Respond concisely and empathetically."))
            chat.append(user(prompt))
            response = chat.sample()
            return response.content.strip()
        except Exception as model_error:
            # Log and try next model
            print(f"Model {model} failed: {str(model_error)}")  # For debugging in console
            if model == models_to_try[-1]:  # Last fallback
                raise model_error

    # This line won't reach if a model succeeds
    raise Exception("All models failed – check your API key or xAI status.")