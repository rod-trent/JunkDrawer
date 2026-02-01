"""
xAI API client for processing natural language queries about Garmin data.
"""

from openai import OpenAI
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XAIClient:
    """Wrapper for xAI API using OpenAI-compatible interface."""
    
    def __init__(self, api_key: str, model: str = "grok-3"):
        """
        Initialize xAI client.
        
        Args:
            api_key: xAI API key
            model: Model to use (default: grok-3)
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        
    def chat(
        self, 
        user_message: str, 
        garmin_context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Send a chat message to xAI with optional Garmin data context.
        
        Args:
            user_message: User's question or message
            garmin_context: Formatted Garmin data to provide as context
            system_prompt: Optional system prompt override
            
        Returns:
            AI's response as a string
        """
        # Default system prompt
        if system_prompt is None:
            system_prompt = """You are a helpful fitness and health assistant with access to the user's Garmin Connect data. 
You help users understand their fitness data, track their progress, and provide insights about their health metrics.

When answering questions:
- Be conversational and friendly
- Provide specific numbers and data when available
- Offer insights and trends when relevant
- Suggest actionable advice when appropriate
- If the data doesn't contain the answer, say so clearly

The user's Garmin data will be provided in the context below."""

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add Garmin context if provided
        if garmin_context:
            context_message = f"Here is the user's current Garmin data:\n\n{garmin_context}"
            messages.append({"role": "system", "content": context_message})
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Call xAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Keep only last 10 exchanges to manage token usage
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error calling xAI API: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def set_model(self, model: str):
        """
        Change the model being used.
        
        Args:
            model: Model name (e.g., "grok-2-1212", "grok-vision-beta")
        """
        self.model = model
        logger.info(f"Model changed to: {model}")
