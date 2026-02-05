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
        
        # Token store directory - garth will create oauth1_token and oauth2_token files
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
                oauth1_path = self.token_store / "oauth1_token"
                oauth2_path = self.token_store / "oauth2_token"
                
                logger.info(f"Checking for token files in: {self.token_store}")
                logger.info(f"OAuth1 token exists: {oauth1_path.exists()}")
                logger.info(f"OAuth2 token exists: {oauth2_path.exists()}")
                
                if not oauth1_path.exists() or not oauth2_path.exists():
                    logger.info("Token files not found, will do fresh login")
                    raise FileNotFoundError("Token files not found")
                
                logger.info(f"Attempting to resume session from: {self.token_store}")
                garth.resume(str(self.token_store))
                logger.info("garth.resume() succeeded")
                
                self.client = Garmin()
                self.client.garth = garth.client
                logger.info("Garmin client initialized with garth.client")
                
                # Try to load the display name and verify session
                try:
                    logger.info("Loading display name...")
                    self.client.get_full_name()
                    logger.info(f"Display name loaded: {self.client.display_name}")
                    
                    # Verify session is valid by getting today's summary
                    from datetime import date
                    today = date.today().strftime('%Y-%m-%d')
                    logger.info(f"Verifying session with user summary for {today}")
                    self.client.get_user_summary(today)
                    
                    self._authenticated = True
                    logger.info("Successfully resumed existing Garmin session")
                    return {'success': True}
                    
                except Exception as verify_error:
                    # Session might be expired, try to refresh the token
                    logger.info(f"Session verification failed, attempting token refresh: {verify_error}")
                    try:
                        logger.info("Attempting to refresh OAuth2 token...")
                        garth.client.refresh_oauth2()
                        garth.save(str(self.token_store))
                        logger.info("Token refreshed and saved")
                        
                        # Try again after refresh
                        self.client.get_full_name()
                        from datetime import date
                        today = date.today().strftime('%Y-%m-%d')
                        self.client.get_user_summary(today)
                        
                        self._authenticated = True
                        logger.info("Successfully refreshed and resumed Garmin session")
                        return {'success': True}
                        
                    except Exception as refresh_error:
                        logger.info(f"Token refresh failed: {refresh_error}")
                        raise  # Fall through to fresh login
                        
            except Exception as resume_error:
                logger.info(f"Could not resume session: {resume_error}")
            
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
                
                # Load the display name so the client has the user ID
                try:
                    self.client.get_full_name()
                except Exception as e:
                    logger.warning(f"Could not load display name: {e}")
                
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
            
            try:
                oauth1_token, oauth2_token = resume_login(self.client_state, mfa_code)
            except Exception as e:
                # If CSRF token error, the session state is stale - need fresh login
                if "CSRF token" in str(e):
                    logger.warning("CSRF token error - session state is stale, attempting fresh login with MFA...")
                    
                    # Do a completely fresh login with MFA
                    result = garth.login(self.email, self.password, return_on_mfa=True)
                    
                    if isinstance(result, tuple) and len(result) == 2:
                        oauth1_token, new_client_state = result
                        self.client_state = new_client_state
                        
                        # Now try resume_login again with fresh state
                        oauth1_token, oauth2_token = resume_login(self.client_state, mfa_code)
                    else:
                        raise Exception("Fresh login didn't return MFA state as expected")
                else:
                    raise
            
            # Set the tokens in garth's global state
            garth.client.oauth1_token = oauth1_token
            garth.client.oauth2_token = oauth2_token
            
            # Try to save tokens - we need to extract just the data, not the methods
            try:
                import time
                
                # Calculate expires_in from expires_at
                current_time = int(time.time())
                expires_at = oauth2_token.expires_at if hasattr(oauth2_token, 'expires_at') else (current_time + 3600)
                refresh_token_expires_at = oauth2_token.refresh_token_expires_at if hasattr(oauth2_token, 'refresh_token_expires_at') else (current_time + 86400)
                
                expires_in = max(0, expires_at - current_time)
                refresh_token_expires_in = max(0, refresh_token_expires_at - current_time)
                
                # Create a clean version of oauth2_token with all required fields (both _in and _at variants)
                clean_oauth2 = {
                    'scope': oauth2_token.scope if hasattr(oauth2_token, 'scope') else '',
                    'jti': oauth2_token.jti if hasattr(oauth2_token, 'jti') else '',
                    'token_type': oauth2_token.token_type if hasattr(oauth2_token, 'token_type') else 'Bearer',
                    'access_token': oauth2_token.access_token if hasattr(oauth2_token, 'access_token') else '',
                    'refresh_token': oauth2_token.refresh_token if hasattr(oauth2_token, 'refresh_token') else '',
                    'expires_in': expires_in,
                    'expires_at': expires_at,
                    'refresh_token_expires_in': refresh_token_expires_in,
                    'refresh_token_expires_at': refresh_token_expires_at,
                }
                
                # Replace oauth2_token with clean version (both for saving and for runtime use)
                from garth.http import OAuth2Token
                garth.client.oauth2_token = OAuth2Token(**clean_oauth2)
                
                garth.save(str(self.token_store))
                logger.info("Tokens saved successfully")
                
            except Exception as save_error:
                logger.warning(f"Could not save tokens (will need to re-auth next time): {save_error}")
                # Continue anyway - authentication still worked
            
            self.client = Garmin()
            self.client.garth = garth.client
            self._authenticated = True
            
            # Load the display name so the client has the user ID
            try:
                self.client.get_full_name()
            except Exception as e:
                logger.warning(f"Could not load display name: {e}")
            
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
            from datetime import date
            
            # Ensure display name is loaded - try multiple times if needed
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if not hasattr(self.client, 'display_name') or self.client.display_name is None:
                        self.client.get_full_name()
                    
                    # Verify we have a display name now
                    if self.client.display_name:
                        break
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to load display name after {max_retries} attempts: {e}")
                        return {}
                    logger.warning(f"Attempt {attempt + 1} to load display name failed, retrying...")
            
            if not self.client.display_name:
                logger.error("Display name is still None, cannot fetch user summary")
                return {}
            
            today = date.today().strftime("%Y-%m-%d")
            return self.client.get_user_summary(today)
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