"""
Garmin Connect data handler for retrieving and formatting user fitness data.
"""

import garth
from garth.exc import GarthHTTPError
from garminconnect import Garmin
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GarminDataHandler:
    """Handles Garmin Connect authentication and data retrieval."""
    
    def __init__(self, email: str, password: str, token_store_path: Optional[str] = None):
        """
        Initialize Garmin Connect handler.
        
        Args:
            email: Garmin Connect email
            password: Garmin Connect password
            token_store_path: Directory to store tokens (default: ~/.garmin_tokens)
        """
        self.email = email
        self.password = password
        self.client: Optional[Garmin] = None
        self._authenticated = False
        
        if token_store_path is None:
            self.token_store = Path.home() / ".garmin_tokens"
        else:
            self.token_store = Path(token_store_path)
        
        self.token_store.mkdir(parents=True, exist_ok=True)
        self.client_state = None
        
    def authenticate(self, mfa_callback: Optional[Callable[[], str]] = None) -> Dict:
        """
        Authenticate with Garmin Connect.
        
        Args:
            mfa_callback: Optional function that returns MFA code when called
        
        Returns:
            Dictionary with authentication status:
            - {'success': True} if successful
            - {'mfa_required': True} if MFA code needed
            - {'error': 'message'} on failure
        """
        try:
            logger.info("Authenticating with Garmin Connect...")
            
            # Try to resume existing session first
            try:
                garth.resume(str(self.token_store))
                self.client = Garmin()
                self.client.garth = garth.client
                
                # Verify session is valid
                self.client.get_user_summary(datetime.now().strftime('%Y-%m-%d'))
                self._authenticated = True
                logger.info("Successfully resumed existing Garmin session")
                return {'success': True}
            except:
                logger.info("No valid saved session, attempting fresh login...")
            
            # Attempt fresh login
            try:
                result = garth.login(self.email, self.password, return_on_mfa=True)
                
                # If result is a tuple, MFA is required
                if isinstance(result, tuple) and len(result) == 2:
                    oauth1_token, client_state = result
                    self.client_state = client_state
                    logger.info("MFA required for Garmin authentication")
                    
                    # If callback provided, complete MFA automatically
                    if mfa_callback:
                        mfa_code = mfa_callback()
                        return self.submit_mfa(mfa_code)
                    
                    return {'mfa_required': True}
                
                # Login succeeded without MFA
                garth.save(str(self.token_store))
                self.client = Garmin()
                self.client.garth = garth.client
                self._authenticated = True
                logger.info("Successfully authenticated with Garmin Connect")
                return {'success': True}
                
            except GarthHTTPError as e:
                logger.error(f"Garmin login failed: {e}")
                return {'error': f'Login failed: {str(e)}'}
                    
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            return {'error': f'Authentication error: {str(e)}'}
    
    def submit_mfa(self, mfa_code: str) -> Dict:
        """
        Submit MFA code after initial authentication indicated MFA required.
        
        Args:
            mfa_code: 6-digit MFA code from user's authenticator
            
        Returns:
            Dictionary with status:
            - {'success': True} on success
            - {'error': 'message'} on failure
        """
        if not self.client_state:
            return {'error': 'Must authenticate first before submitting MFA'}
        
        try:
            logger.info("Submitting MFA code to Garmin...")
            
            # Resume login with MFA code - it's in the sso submodule
            # This returns the OAuth tokens
            from garth.sso import resume_login
            oauth1_token, oauth2_token = resume_login(self.client_state, mfa_code)
            
            # Set the tokens in garth's global state
            garth.client.oauth1_token = oauth1_token
            garth.client.oauth2_token = oauth2_token
            
            # Try to save tokens, but don't fail if it errors
            try:
                garth.save(str(self.token_store))
                logger.info("Tokens saved successfully")
            except Exception as save_error:
                logger.warning(f"Could not save tokens (will need to re-auth next time): {save_error}")
                # Continue anyway - authentication still worked
            
            self.client = Garmin()
            self.client.garth = garth.client
            self._authenticated = True
            
            logger.info("Successfully authenticated with MFA")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"MFA submission failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {'error': f'MFA submission failed: {str(e)}'}
    
    def _ensure_authenticated(self):
        """Ensure client is authenticated before making requests."""
        if not self._authenticated or self.client is None:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
    
    def get_user_summary(self) -> Dict:
        """
        Get user profile summary.
        
        Returns:
            Dictionary containing user profile information
        """
        self._ensure_authenticated()
        try:
            return self.client.get_user_summary(datetime.now().strftime("%Y-%m-%d"))
        except Exception as e:
            logger.error(f"Error fetching user summary: {e}")
            return {}
    
    def get_activities(self, limit: int = 10) -> List[Dict]:
        """
        Get recent activities.
        
        Args:
            limit: Number of activities to retrieve
            
        Returns:
            List of activity dictionaries
        """
        self._ensure_authenticated()
        try:
            activities = self.client.get_activities(0, limit)
            return activities if activities else []
        except Exception as e:
            logger.error(f"Error fetching activities: {e}")
            return []
    
    def get_steps_data(self, date: Optional[str] = None) -> Dict:
        """
        Get steps data for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing steps data
        """
        self._ensure_authenticated()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            return self.client.get_steps_data(date)
        except Exception as e:
            logger.error(f"Error fetching steps data: {e}")
            return {}
    
    def get_heart_rate_data(self, date: Optional[str] = None) -> Dict:
        """
        Get heart rate data for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing heart rate data
        """
        self._ensure_authenticated()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            return self.client.get_heart_rates(date)
        except Exception as e:
            logger.error(f"Error fetching heart rate data: {e}")
            return {}
    
    def get_sleep_data(self, date: Optional[str] = None) -> Dict:
        """
        Get sleep data for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing sleep data
        """
        self._ensure_authenticated()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            return self.client.get_sleep_data(date)
        except Exception as e:
            logger.error(f"Error fetching sleep data: {e}")
            return {}
    
    def get_body_composition(self, date: Optional[str] = None) -> Dict:
        """
        Get body composition data.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing body composition data
        """
        self._ensure_authenticated()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            return self.client.get_body_composition(date)
        except Exception as e:
            logger.error(f"Error fetching body composition: {e}")
            return {}
    
    def format_data_for_context(self, data_type: str = "summary") -> str:
        """
        Format Garmin data into a readable string for LLM context.
        
        Args:
            data_type: Type of data to format ("summary", "activities", "steps", etc.)
            
        Returns:
            Formatted string containing the requested data
        """
        self._ensure_authenticated()
        
        context_parts = []
        today = datetime.now().strftime("%Y-%m-%d")
        
        if data_type == "summary" or data_type == "all":
            # Get user summary
            summary = self.get_user_summary()
            if summary:
                context_parts.append("=== Today's Summary ===")
                context_parts.append(f"Date: {today}")
                if "totalSteps" in summary:
                    context_parts.append(f"Steps: {summary.get('totalSteps', 'N/A')}")
                if "totalKilocalories" in summary:
                    context_parts.append(f"Calories: {summary.get('totalKilocalories', 'N/A')}")
                if "activeKilocalories" in summary:
                    context_parts.append(f"Active Calories: {summary.get('activeKilocalories', 'N/A')}")
                context_parts.append("")
        
        if data_type == "activities" or data_type == "all":
            # Get recent activities
            activities = self.get_activities(5)
            if activities:
                context_parts.append("=== Recent Activities (Last 5) ===")
                for i, activity in enumerate(activities, 1):
                    act_name = activity.get("activityName", "Unknown")
                    act_type = activity.get("activityType", {}).get("typeKey", "Unknown")
                    distance = activity.get("distance", 0) / 1000 if activity.get("distance") else 0  # Convert to km
                    duration = activity.get("duration", 0) / 60 if activity.get("duration") else 0  # Convert to minutes
                    calories = activity.get("calories", "N/A")
                    start_time = activity.get("startTimeLocal", "N/A")
                    
                    context_parts.append(f"{i}. {act_name} ({act_type})")
                    context_parts.append(f"   Date: {start_time}")
                    context_parts.append(f"   Distance: {distance:.2f} km")
                    context_parts.append(f"   Duration: {duration:.1f} minutes")
                    context_parts.append(f"   Calories: {calories}")
                    context_parts.append("")
        
        if data_type == "sleep" or data_type == "all":
            # Get sleep data
            sleep = self.get_sleep_data()
            if sleep and "dailySleepDTO" in sleep:
                sleep_data = sleep["dailySleepDTO"]
                context_parts.append("=== Last Night's Sleep ===")
                sleep_seconds = sleep_data.get("sleepTimeSeconds", 0)
                sleep_hours = sleep_seconds / 3600 if sleep_seconds else 0
                context_parts.append(f"Total Sleep: {sleep_hours:.1f} hours")
                context_parts.append(f"Deep Sleep: {sleep_data.get('deepSleepSeconds', 0) / 3600:.1f} hours")
                context_parts.append(f"Light Sleep: {sleep_data.get('lightSleepSeconds', 0) / 3600:.1f} hours")
                context_parts.append(f"REM Sleep: {sleep_data.get('remSleepSeconds', 0) / 3600:.1f} hours")
                context_parts.append(f"Awake Time: {sleep_data.get('awakeSleepSeconds', 0) / 3600:.1f} hours")
                context_parts.append("")
        
        return "\n".join(context_parts) if context_parts else "No data available"
