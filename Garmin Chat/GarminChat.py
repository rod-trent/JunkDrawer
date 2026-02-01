"""
Garmin Chat - A local GenAI chatbot for querying Garmin Connect data.
"""

import gradio as gr
import os
from dotenv import load_dotenv
from garmin_handler import GarminDataHandler
from xai_client import XAIClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Global state
garmin_handler = None
xai_client = None
authenticated = False
mfa_required = False


def initialize_clients():
    """Initialize Garmin and xAI clients."""
    global garmin_handler, xai_client, authenticated, mfa_required
    
    # Get credentials from environment
    xai_api_key = os.getenv("XAI_API_KEY")
    garmin_email = os.getenv("GARMIN_EMAIL")
    garmin_password = os.getenv("GARMIN_PASSWORD")
    
    if not xai_api_key:
        return "❌ Error: XAI_API_KEY not found in .env file"
    
    if not garmin_email or not garmin_password:
        return "❌ Error: GARMIN_EMAIL or GARMIN_PASSWORD not found in .env file"
    
    # Initialize xAI client
    try:
        xai_client = XAIClient(xai_api_key)
        logger.info("xAI client initialized")
    except Exception as e:
        return f"❌ Error initializing xAI client: {e}"
    
    # Initialize and authenticate Garmin
    try:
        garmin_handler = GarminDataHandler(garmin_email, garmin_password)
        result = garmin_handler.authenticate()
        
        if result.get('success'):
            authenticated = True
            mfa_required = False
            return "✅ Successfully connected to Garmin Connect and xAI!"
        elif result.get('mfa_required'):
            mfa_required = True
            authenticated = False
            return "🔐 MFA Required: Please enter your 6-digit code from your authenticator app in the MFA Code field below, then click 'Submit MFA Code'."
        else:
            return f"❌ Failed to authenticate with Garmin Connect: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"❌ Error with Garmin Connect: {e}"


def submit_mfa_code(mfa_code):
    """Submit MFA code to complete Garmin authentication."""
    global garmin_handler, authenticated, mfa_required
    
    if not mfa_required:
        return "❌ MFA not required. Please connect to Garmin first."
    
    if not garmin_handler:
        return "❌ Please click 'Connect to Garmin' first."
    
    if not mfa_code or len(mfa_code) != 6:
        return "❌ Please enter a valid 6-digit MFA code."
    
    try:
        result = garmin_handler.submit_mfa(mfa_code)
        
        if result.get('success'):
            authenticated = True
            mfa_required = False
            return "✅ MFA successful! You can now chat about your Garmin data."
        else:
            return f"❌ MFA failed: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"❌ Error submitting MFA: {e}"


def chat_response(message, history):
    """
    Process chat messages and return responses.
    
    Args:
        message: User's message
        history: Chat history (handled by Gradio)
        
    Returns:
        Response from xAI
    """
    global garmin_handler, xai_client, authenticated
    
    if not authenticated:
        return "Please authenticate first by clicking the 'Connect to Garmin' button above."
    
    # Determine what Garmin data to fetch based on the query
    garmin_context = None
    query_lower = message.lower()
    
    # Fetch relevant data based on keywords
    if any(word in query_lower for word in ["activity", "activities", "workout", "run", "walk", "bike", "exercise"]):
        garmin_context = garmin_handler.format_data_for_context("activities")
    elif any(word in query_lower for word in ["sleep", "rest", "bed"]):
        garmin_context = garmin_handler.format_data_for_context("sleep")
    elif any(word in query_lower for word in ["step", "walk", "distance", "calorie"]):
        garmin_context = garmin_handler.format_data_for_context("summary")
    else:
        # Default to summary for general queries
        garmin_context = garmin_handler.format_data_for_context("all")
    
    # Get response from xAI
    response = xai_client.chat(message, garmin_context)
    return response


def refresh_data():
    """Force refresh of Garmin data."""
    global garmin_handler, authenticated
    
    if not authenticated:
        return "Not connected to Garmin. Please authenticate first."
    
    try:
        # Re-authenticate to refresh session
        result = garmin_handler.authenticate()
        if result.get('success'):
            return "✅ Data refreshed successfully!"
        else:
            return f"❌ Failed to refresh data: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"❌ Error refreshing data: {e}"


def reset_chat():
    """Reset the conversation history."""
    global xai_client
    
    if xai_client:
        xai_client.reset_conversation()
        return "✅ Conversation reset!"
    return "No active session to reset."


# Create Gradio interface
with gr.Blocks(title="Garmin Chat") as app:
    gr.Markdown(
        """
        # 🏃‍♂️ Garmin Chat
        
        Ask questions about your Garmin fitness data! This chatbot connects to your Garmin Connect account
        and uses AI to help you understand your activities, sleep, steps, and more.
        
        **Examples:**
        - "How many steps did I take today?"
        - "What was my last workout?"
        - "How did I sleep last night?"
        - "Show me my recent activities"
        - "What are my calorie statistics?"
        """
    )
    
    with gr.Row():
        auth_button = gr.Button("🔐 Connect to Garmin", variant="primary")
        refresh_button = gr.Button("🔄 Refresh Data")
        reset_button = gr.Button("🗑️ Reset Chat")
    
    status_output = gr.Textbox(label="Status", interactive=False)
    
    # MFA input (only shown when needed)
    with gr.Row():
        mfa_input = gr.Textbox(
            label="MFA Code (if required)",
            placeholder="Enter 6-digit code from authenticator app",
            max_length=6,
            visible=True
        )
        mfa_button = gr.Button("🔑 Submit MFA Code", visible=True)
    
    # Chat interface
    chatbot = gr.ChatInterface(
        fn=chat_response,
        chatbot=gr.Chatbot(height=500),
        textbox=gr.Textbox(placeholder="Ask about your Garmin data...", container=False),
        examples=[
            "How many steps did I take today?",
            "What was my last workout?",
            "How did I sleep last night?",
            "Show me my recent activities",
            "What's my average heart rate?",
        ]
    )
    
    # Wire up buttons
    auth_button.click(fn=initialize_clients, outputs=status_output)
    mfa_button.click(fn=submit_mfa_code, inputs=mfa_input, outputs=status_output)
    refresh_button.click(fn=refresh_data, outputs=status_output)
    reset_button.click(fn=reset_chat, outputs=status_output)
    
    gr.Markdown(
        """
        ---
        **Note:** Your Garmin credentials and xAI API key should be stored in a `.env` file in the same directory.
        See `.env.example` for the required format.
        """
    )


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏃‍♂️ Garmin Chat")
    print("="*60)
    print("\nStarting Gradio interface...")
    print("Make sure your .env file is configured with:")
    print("  - XAI_API_KEY")
    print("  - GARMIN_EMAIL")
    print("  - GARMIN_PASSWORD")
    print("\nThe app will open in your browser shortly...")
    print("="*60 + "\n")
    
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )
