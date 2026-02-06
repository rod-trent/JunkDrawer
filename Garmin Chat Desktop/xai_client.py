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

AVAILABLE DATA TYPES:
The system can access the following Garmin data:
- Activities (runs, walks, bike rides, workouts, etc.)
- Sleep data (total, deep, light, REM, awake time)
- Steps and distance
- Heart rate (resting, active, zones)
- Body Battery (energy levels throughout the day)
- Stress levels (average, rest, activity, duration by intensity)
- Respiration rate (waking and sleeping)
- Hydration (water intake)
- Nutrition (calories consumed and burned)
- Floors climbed (ascended and descended)
- Intensity minutes (moderate and vigorous activity)
- Blood oxygen / SpO2 (pulse oximetry)
- Heart Rate Variability (HRV)
- VO2 Max and fitness age
- Training status and load
- Body composition

IMPORTANT DATA CONTEXT:
- The activity data shows the user's most recent activities (typically 5-30 depending on the query)
- Activities are ordered by date (newest first)
- The number of activities shown does NOT necessarily correspond to a specific time period
  * For example: 30 activities might only span 10 days if the user works out frequently
  * Or 30 activities might span several months if the user exercises less often
- When the user asks about "last 30 days" or "this month", understand they want a TIME PERIOD, not just 30 activities
- If you see activities that don't cover the requested time period, tell them you need to look at a specific date range

When users ask about TIME PERIODS (like "last 30 days", "this month", "last week"):
- Look at the dates in the activity data to see what time span is actually covered
- If the activities shown don't cover the full period requested, say: "The activities shown cover [actual date range]. To analyze the full [requested period], I'd need to look at activities from [start date] to [end date]. Would you like me to do that?"
- Be specific about what dates the current data covers

When users ask about ACTIVITY COUNTS (like "last 10 runs", "my recent workouts"):
- Use the activities provided and give them what they asked for
- Don't worry about date ranges in this case

When users ask about HEALTH METRICS (Body Battery, stress, HRV, etc.):
- Provide the specific numbers and explain what they mean
- Offer context on whether the values are good/normal
- Suggest factors that might influence these metrics
- Connect metrics when relevant (e.g., low Body Battery and high stress often correlate)

When answering questions:
- Be conversational and friendly
- Provide specific numbers and data when available
- Be precise about date ranges - check the actual dates in the activity data
- Offer insights and trends when relevant
- Suggest actionable advice when appropriate
- If you need more data or a different date range, clearly explain what you need
- NEVER apologize for limitations - instead, explain what you CAN do
- When discussing health metrics like Body Battery or stress, provide context and interpretation

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