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
                
                logger.info(f"Token store directory: {self.token_store}")
                logger.info(f"OAuth1 token path: {oauth1_path}")
                logger.info(f"OAuth2 token path: {oauth2_path}")
                logger.info(f"OAuth1 token exists: {oauth1_path.exists()}")
                logger.info(f"OAuth2 token exists: {oauth2_path.exists()}")
                
                if oauth1_path.exists():
                    logger.info(f"OAuth1 token file size: {oauth1_path.stat().st_size} bytes")
                if oauth2_path.exists():
                    logger.info(f"OAuth2 token file size: {oauth2_path.stat().st_size} bytes")
                
                if not oauth1_path.exists() or not oauth2_path.exists():
                    logger.info("Token files not found, will do fresh login")
                    raise FileNotFoundError("Token files not found")
                
                logger.info(f"Calling garth.resume() with path: {str(self.token_store)}")
                try:
                    garth.resume(str(self.token_store))
                    logger.info("✅ garth.resume() succeeded!")
                except Exception as resume_ex:
                    logger.error(f"❌ garth.resume() failed: {type(resume_ex).__name__}: {resume_ex}")
                    
                    # Try manual token loading
                    logger.info("Attempting manual token load...")
                    import json
                    import os
                    
                    token_dir = str(self.token_store)
                    oauth1_path = os.path.join(token_dir, "oauth1_token")
                    oauth2_path = os.path.join(token_dir, "oauth2_token")
                    
                    if os.path.exists(oauth1_path) and os.path.exists(oauth2_path):
                        try:
                            # Load OAuth1 token
                            with open(oauth1_path, 'r') as f:
                                oauth1_data = json.load(f)
                            logger.info("✅ Loaded OAuth1 token manually")
                            
                            # Load OAuth2 token
                            with open(oauth2_path, 'r') as f:
                                oauth2_data = json.load(f)
                            logger.info("✅ Loaded OAuth2 token manually")
                            
                            # Set tokens in garth client
                            from garth.http import OAuth1Token, OAuth2Token
                            garth.client.oauth1_token = OAuth1Token(**oauth1_data)
                            garth.client.oauth2_token = OAuth2Token(**oauth2_data)
                            logger.info("✅ Manually loaded tokens into garth.client")
                            
                        except Exception as manual_load_error:
                            logger.error(f"Failed to manually load tokens: {manual_load_error}")
                            raise
                    else:
                        raise
                
                logger.info("Creating Garmin client...")
                self.client = Garmin()
                self.client.garth = garth.client
                logger.info("✅ Garmin client initialized with garth.client")
                
                # Try to load the display name and verify session
                try:
                    logger.info("Loading display name...")
                    
                    # Try to load display name but don't fail if it doesn't work
                    # It will be populated on first API call
                    try:
                        self.client.get_full_name()
                        logger.info(f"Display name after get_full_name(): {self.client.display_name}")
                    except Exception as name_error:
                        logger.info(f"get_full_name() didn't populate display_name: {name_error}")
                    
                    # Don't fail if display_name is None - it will be set on first real API call
                    # Just verify the session works by trying a simple API call
                    logger.info("Verifying session with a test API call...")
                    try:
                        # Try to get activities which doesn't need display_name
                        activities = self.client.get_activities(0, 1)  # Get just 1 activity as a test
                        logger.info("✅ Session verified - API call succeeded")
                    except Exception as verify_error:
                        logger.info(f"Session verification failed: {verify_error}")
                        raise
                    
                    self._authenticated = True
                    logger.info("✅ Successfully resumed existing Garmin session")
                    return {'success': True}
                    
                except Exception as verify_error:
                    # Session might be expired, try to refresh the token
                    logger.info(f"⚠️ Session verification failed: {type(verify_error).__name__}: {verify_error}")
                    logger.info("Attempting token refresh...")
                    try:
                        logger.info("Calling garth.client.refresh_oauth2()...")
                        garth.client.refresh_oauth2()
                        logger.info("✅ Token refreshed, saving...")
                        garth.save(str(self.token_store))
                        logger.info("✅ Refreshed tokens saved")
                        
                        # Try again after refresh
                        logger.info("Retrying after refresh...")
                        
                        # Try to load display name but don't require it
                        try:
                            self.client.get_full_name()
                        except:
                            pass
                        
                        # Just verify session works
                        logger.info("Verifying refreshed session...")
                        activities = self.client.get_activities(0, 1)
                        logger.info("✅ Refreshed session verified")
                        
                        self._authenticated = True
                        logger.info("✅ Successfully refreshed and resumed Garmin session")
                        return {'success': True}
                        
                    except Exception as refresh_error:
                        logger.error(f"❌ Token refresh failed: {type(refresh_error).__name__}: {refresh_error}")
                        raise  # Fall through to fresh login
                        
            except Exception as resume_error:
                logger.info(f"❌ Could not resume session: {type(resume_error).__name__}: {resume_error}")
                logger.info("Will attempt fresh login...")
            
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
                
                logger.info(f"Preparing to save tokens to: {self.token_store}")
                
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
                
                logger.info(f"Created clean OAuth2 token with expires_in={expires_in}, expires_at={expires_at}")
                
                # Replace oauth2_token with clean version (both for saving and for runtime use)
                from garth.http import OAuth2Token
                garth.client.oauth2_token = OAuth2Token(**clean_oauth2)
                logger.info("Set garth.client.oauth2_token to clean version")
                
                logger.info(f"Calling garth.save('{str(self.token_store)}')")
                
                # Try garth's native save first
                try:
                    garth.save(str(self.token_store))
                    logger.info("✅ garth.save() completed")
                except Exception as garth_save_error:
                    logger.warning(f"garth.save() error: {garth_save_error}")
                
                # MANUAL TOKEN SAVE as backup - write the tokens ourselves
                import json
                import os
                
                token_dir = str(self.token_store)
                os.makedirs(token_dir, exist_ok=True)
                
                # Save OAuth1 token
                oauth1_path = os.path.join(token_dir, "oauth1_token")
                try:
                    oauth1_data = {
                        'oauth_token': oauth1_token[0] if isinstance(oauth1_token, tuple) else getattr(oauth1_token, 'oauth_token', str(oauth1_token)),
                        'oauth_token_secret': oauth1_token[1] if isinstance(oauth1_token, tuple) else getattr(oauth1_token, 'oauth_token_secret', ''),
                    }
                    with open(oauth1_path, 'w') as f:
                        json.dump(oauth1_data, f, indent=2)
                    logger.info(f"✅ Manually saved OAuth1 token to: {oauth1_path}")
                except Exception as oauth1_error:
                    logger.error(f"Failed to manually save OAuth1 token: {oauth1_error}")
                
                # Save OAuth2 token  
                oauth2_path = os.path.join(token_dir, "oauth2_token")
                try:
                    oauth2_data = clean_oauth2  # Use the clean version we already created
                    with open(oauth2_path, 'w') as f:
                        json.dump(oauth2_data, f, indent=2)
                    logger.info(f"✅ Manually saved OAuth2 token to: {oauth2_path}")
                except Exception as oauth2_error:
                    logger.error(f"Failed to manually save OAuth2 token: {oauth2_error}")
                
                # Verify files were actually created
                oauth1_path = self.token_store / "oauth1_token"
                oauth2_path = self.token_store / "oauth2_token"
                logger.info(f"Verifying token files were created...")
                logger.info(f"OAuth1 exists after save: {oauth1_path.exists()}")
                logger.info(f"OAuth2 exists after save: {oauth2_path.exists()}")
                
                if oauth1_path.exists() and oauth2_path.exists():
                    logger.info("✅ Tokens saved successfully and verified!")
                else:
                    logger.error("⚠️ garth.save() succeeded but files were not created!")
                
            except Exception as save_error:
                logger.warning(f"Could not save tokens (will need to re-auth next time): {save_error}")
                import traceback
                logger.warning(f"Traceback: {traceback.format_exc()}")
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
    
    def _ensure_display_name(self):
        """
        Ensure display_name is set for API calls that require it.
        This is a workaround for the garminconnect library's display_name issue.
        """
        if not hasattr(self.client, 'display_name') or self.client.display_name is None:
            logger.debug("Display name not set, attempting to load it...")
            
            # Method 1: Try get_full_name()
            try:
                self.client.get_full_name()
                if self.client.display_name:
                    logger.debug(f"Display name loaded: {self.client.display_name}")
                    return
            except Exception as e:
                logger.debug(f"get_full_name() failed: {e}")
            
            # Method 2: Use email as fallback
            try:
                self.client.display_name = self.email.split('@')[0]
                logger.debug(f"Using fallback display name from email: {self.client.display_name}")
                return
            except Exception as e:
                logger.debug(f"Email fallback failed: {e}")
            
            # If still None, log warning
            logger.debug("Could not set display_name, some API calls may fail")
    
    def get_user_summary(self) -> Dict:
        """
        Get user profile summary.
        
        Returns:
            Dictionary containing user profile information
        """
        self._ensure_authenticated()
        try:
            from datetime import date
            
            # The display_name issue is a known quirk with garminconnect library
            # Try multiple methods to populate it
            
            # Method 1: Try get_full_name()
            if not hasattr(self.client, 'display_name') or self.client.display_name is None:
                try:
                    self.client.get_full_name()
                    if self.client.display_name:
                        logger.info(f"✅ Display name loaded via get_full_name(): {self.client.display_name}")
                except Exception as e:
                    logger.debug(f"get_full_name() failed: {e}")
            
            # Method 2: Try loading from user stats if still None
            if not self.client.display_name:
                try:
                    today = date.today().strftime("%Y-%m-%d")
                    stats = self.client.get_stats(today)
                    if stats and 'userName' in stats:
                        self.client.display_name = stats['userName']
                        logger.info(f"✅ Display name loaded from stats: {self.client.display_name}")
                except Exception as e:
                    logger.debug(f"Stats method failed: {e}")
            
            # Method 3: Use email as fallback display name
            if not self.client.display_name:
                try:
                    self.client.display_name = self.email.split('@')[0]
                    logger.info(f"⚠️ Using fallback display name from email: {self.client.display_name}")
                except Exception as e:
                    logger.debug(f"Email fallback failed: {e}")
            
            # If still None, log warning but try anyway (some endpoints might work)
            if not self.client.display_name:
                logger.warning("Display name is still None, attempting get_user_summary anyway...")
            
            today = date.today().strftime("%Y-%m-%d")
            return self.client.get_user_summary(today)
            
        except Exception as e:
            logger.error(f"Error fetching user summary: {e}")
            return {}
    
    def get_activities(self, limit: int = 10, start: int = 0) -> List[Dict]:
        """
        Get recent activities with pagination support.
        
        Args:
            limit: Number of activities to retrieve (max recommended: 100)
            start: Starting index for pagination (0 = most recent)
            
        Returns:
            List of activity dictionaries
            
        Note:
            - Garmin API can return up to 100 activities per request
            - For more than 100, use multiple requests with different start values
            - Activities are ordered newest to oldest
        """
        self._ensure_authenticated()
        try:
            activities = self.client.get_activities(start, limit)
            return activities if activities else []
        except Exception as e:
            logger.error(f"Error fetching activities: {e}")
            return []
    
    def get_activities_by_date(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get activities within a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of activity dictionaries within the date range
            
        Note:
            This fetches activities in batches and filters by date.
            May require multiple API calls for large date ranges.
        """
        self._ensure_authenticated()
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            all_activities = []
            batch_size = 50
            current_start = 0
            
            # Keep fetching until we get activities outside our date range
            while True:
                activities = self.get_activities(limit=batch_size, start=current_start)
                
                if not activities:
                    break
                
                for activity in activities:
                    # Parse activity date
                    start_time_str = activity.get("startTimeLocal", "")
                    if start_time_str:
                        activity_dt = datetime.strptime(start_time_str[:10], "%Y-%m-%d")
                        
                        # If activity is within range, add it
                        if start_dt <= activity_dt <= end_dt:
                            all_activities.append(activity)
                        # If we've gone past the start date, we're done
                        elif activity_dt < start_dt:
                            return all_activities
                
                # Move to next batch
                current_start += batch_size
                
                # Safety limit: don't fetch more than 500 activities
                if current_start >= 500:
                    logger.warning("Reached safety limit of 500 activities")
                    break
            
            return all_activities
            
        except Exception as e:
            logger.error(f"Error fetching activities by date: {e}")
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
    
    def get_body_battery(self, date: Optional[str] = None) -> Dict:
        """
        Get Body Battery data (energy levels throughout the day).
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing Body Battery data with charged/drained values
        """
        self._ensure_authenticated()
        self._ensure_display_name()  # Ensure display_name is set
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            # Try to get Body Battery data from available API
            # Body Battery may not be available for all devices
            data = self.client.get_body_battery(date)
            if data:
                return {
                    'date': date,
                    'charged': data.get('bodyBatteryChargedValue', 0),
                    'drained': data.get('bodyBatteryDrainedValue', 0),
                    'highest': data.get('bodyBatteryHighestValue', 0),
                    'lowest': data.get('bodyBatteryLowestValue', 0),
                    'current': data.get('bodyBatteryMostRecentValue', 0)
                }
            return {}
        except AttributeError:
            # Method doesn't exist in this version of garminconnect
            logger.debug("Body Battery API not available")
            return {}
        except Exception as e:
            logger.debug(f"Body Battery not available: {e}")
            return {}
    
    def get_stress_data(self, date: Optional[str] = None) -> Dict:
        """
        Get stress level data for the day.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing stress levels (0-100 scale)
        """
        self._ensure_authenticated()
        self._ensure_display_name()  # Ensure display_name is set
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            # Try to get stress data
            data = self.client.get_stress_data(date)
            if data and isinstance(data, dict):
                return {
                    'date': date,
                    'average': data.get('averageStressLevel', 0),
                    'max': data.get('maxStressLevel', 0),
                    'rest': data.get('restStressLevel', 0),
                    'activity': data.get('activityStressLevel', 0),
                    'low_duration': data.get('lowStressDuration', 0),
                    'medium_duration': data.get('mediumStressDuration', 0),
                    'high_duration': data.get('highStressDuration', 0)
                }
            return {}
        except AttributeError:
            logger.debug("Stress data API not available")
            return {}
        except Exception as e:
            logger.debug(f"Stress data not available: {e}")
            return {}
    
    def get_respiration_data(self, date: Optional[str] = None) -> Dict:
        """
        Get respiration rate data (breaths per minute).
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing respiration rates
        """
        self._ensure_authenticated()
        self._ensure_display_name()  # Ensure display_name is set
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            data = self.client.get_respiration_data(date)
            if data:
                return {
                    'date': date,
                    'waking_avg': data.get('avgWakingRespirationValue', 0),
                    'sleeping_avg': data.get('avgSleepRespirationValue', 0),
                    'highest': data.get('highestRespirationValue', 0),
                    'lowest': data.get('lowestRespirationValue', 0)
                }
            return {}
        except AttributeError:
            logger.debug("Respiration API not available")
            return {}
        except Exception as e:
            logger.debug(f"Respiration data not available: {e}")
            return {}
    
    def get_hydration_data(self, date: Optional[str] = None) -> Dict:
        """
        Get hydration/water intake data.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing hydration data in milliliters
        """
        self._ensure_authenticated()
        self._ensure_display_name()  # Ensure display_name is set
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            return self.client.get_hydration_data(date) or {}
        except AttributeError:
            logger.debug("Hydration API not available")
            return {}
        except Exception as e:
            logger.debug(f"Hydration data not available: {e}")
            return {}
    
    def get_floors_data(self, date: Optional[str] = None) -> Dict:
        """
        Get floors climbed data.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing floors climbed
        """
        self._ensure_authenticated()
        self._ensure_display_name()  # Ensure display_name is set
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            # Floors are usually in the daily summary
            steps_data = self.client.get_steps_data(date)
            if steps_data:
                return {
                    'date': date,
                    'floors_ascended': steps_data.get('floorsAscended', 0),
                    'floors_descended': steps_data.get('floorsDescended', 0),
                    'floors_ascended_goal': steps_data.get('floorsAscendedGoal', 0)
                }
            return {}
        except Exception as e:
            logger.debug(f"Floors data not available: {e}")
            return {}
    
    def get_intensity_minutes(self, date: Optional[str] = None) -> Dict:
        """
        Get intensity minutes (moderate and vigorous activity).
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing intensity minutes
        """
        self._ensure_authenticated()
        self._ensure_display_name()  # Ensure display_name is set
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            # Try to get from heart rate data which sometimes includes intensity
            hr_data = self.client.get_heart_rates(date)
            if hr_data and isinstance(hr_data, dict):
                return {
                    'date': date,
                    'moderate': hr_data.get('moderateIntensityMinutes', 0),
                    'vigorous': hr_data.get('vigorousIntensityMinutes', 0),
                    'weekly_moderate': hr_data.get('weeklyModerateIntensityMinutes', 0),
                    'weekly_vigorous': hr_data.get('weeklyVigorousIntensityMinutes', 0),
                    'weekly_goal': hr_data.get('intensityMinutesGoal', 150)
                }
            return {}
        except Exception as e:
            logger.debug(f"Intensity minutes not available: {e}")
            return {}
    
    def get_calories_data(self, date: Optional[str] = None) -> Dict:
        """
        Get calories data (consumed, burned, net).
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing calorie data
        """
        self._ensure_authenticated()
        self._ensure_display_name()  # Ensure display_name is set
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            # Get from user summary which has calorie data
            summary = self.get_user_summary()
            if summary:
                return {
                    'date': date,
                    'total_burned': summary.get('totalKilocalories', 0),
                    'active_burned': summary.get('activeKilocalories', 0),
                    'bmr': summary.get('bmrKilocalories', 0),
                    'consumed': summary.get('consumedCalories', 0),
                    'net': summary.get('netCalorieGoal', 0)
                }
            return {}
        except Exception as e:
            logger.debug(f"Calorie data not available: {e}")
            return {}
    
    def get_nutrition_summary(self, date: Optional[str] = None) -> Dict:
        """
        Get detailed nutrition summary including macros and food logging.
        This is Garmin's newer nutrition feature.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing nutrition data (calories, protein, carbs, fat, etc.)
        """
        self._ensure_authenticated()
        self._ensure_display_name()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        nutrition_data = {}
        
        # Try Method 1: Dedicated nutrition API endpoint
        try:
            # Some Garmin devices support a nutrition summary endpoint
            data = self.client.get_nutrition_summary(date)
            if data:
                nutrition_data.update({
                    'date': date,
                    'calories_consumed': data.get('totalCalories', data.get('consumedCalories', 0)),
                    'protein_g': data.get('totalProtein', 0),
                    'carbs_g': data.get('totalCarbs', 0),
                    'fat_g': data.get('totalFat', 0),
                    'fiber_g': data.get('totalFiber', 0),
                    'sugar_g': data.get('totalSugar', 0),
                    'sodium_mg': data.get('totalSodium', 0),
                    'water_ml': data.get('totalWater', 0)
                })
                logger.debug("Nutrition data loaded from get_nutrition_summary")
                return nutrition_data
        except AttributeError:
            logger.debug("get_nutrition_summary method not available")
        except Exception as e:
            logger.debug(f"get_nutrition_summary failed: {e}")
        
        # Try Method 2: Daily summary which sometimes includes nutrition
        try:
            summary = self.client.get_user_summary(date)
            if summary and 'consumedCalories' in summary:
                nutrition_data.update({
                    'date': date,
                    'calories_consumed': summary.get('consumedCalories', 0),
                    'calories_goal': summary.get('netCalorieGoal', 0)
                })
                logger.debug("Basic nutrition data from user summary")
        except Exception as e:
            logger.debug(f"User summary nutrition failed: {e}")
        
        # Try Method 3: Stats endpoint
        try:
            stats = self.client.get_stats(date)
            if stats:
                if 'consumedCalories' in stats:
                    nutrition_data['calories_consumed'] = stats.get('consumedCalories', 0)
                if 'netCalorieGoal' in stats:
                    nutrition_data['calories_goal'] = stats.get('netCalorieGoal', 0)
                logger.debug("Nutrition data from stats endpoint")
        except Exception as e:
            logger.debug(f"Stats endpoint nutrition failed: {e}")
        
        return nutrition_data if nutrition_data else {}
    
    def get_food_log(self, date: Optional[str] = None) -> List[Dict]:
        """
        Get detailed food log entries for a specific date.
        This retrieves individual meals/snacks logged in Garmin.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            List of food entries with nutrition details
        """
        self._ensure_authenticated()
        self._ensure_display_name()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Try to get food log - this may be a newer API endpoint
            food_log = self.client.get_food_log(date)
            if food_log and isinstance(food_log, list):
                return food_log
            return []
        except AttributeError:
            logger.debug("get_food_log method not available in this version")
            return []
        except Exception as e:
            logger.debug(f"Food log not available: {e}")
            return []
    
    def get_spo2_data(self, date: Optional[str] = None) -> Dict:
        """
        Get blood oxygen (SpO2/Pulse Ox) data.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing SpO2 percentages
        """
        self._ensure_authenticated()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            return self.client.get_spo2_data(date) or {}
        except AttributeError:
            logger.debug("SpO2 API not available")
            return {}
        except Exception as e:
            logger.debug(f"SpO2 data not available: {e}")
            return {}
    
    def get_max_metrics(self) -> Dict:
        """
        Get max performance metrics (VO2 Max, lactate threshold, etc).
        
        Returns:
            Dictionary containing max performance metrics
        """
        self._ensure_authenticated()
        try:
            return self.client.get_max_metrics() or {}
        except AttributeError:
            logger.debug("Max metrics API not available")
            return {}
        except Exception as e:
            logger.debug(f"Max metrics not available: {e}")
            return {}
    
    def get_training_status(self) -> Dict:
        """
        Get training status and recommendations.
        
        Returns:
            Dictionary containing training load, status, and recommendations
        """
        self._ensure_authenticated()
        try:
            return self.client.get_training_status() or {}
        except AttributeError:
            logger.debug("Training status API not available")
            return {}
        except Exception as e:
            logger.debug(f"Training status not available: {e}")
            return {}
    
    def get_training_readiness(self, date: Optional[str] = None) -> Dict:
        """
        Get training readiness score (combines multiple metrics).
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing training readiness score and factors
        """
        self._ensure_authenticated()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            return self.client.get_training_readiness(date) or {}
        except AttributeError:
            logger.debug("Training readiness API not available")
            return {}
        except Exception as e:
            logger.debug(f"Training readiness not available: {e}")
            return {}
    
    def get_hrv_data(self, date: Optional[str] = None) -> Dict:
        """
        Get Heart Rate Variability (HRV) data.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary containing HRV metrics
        """
        self._ensure_authenticated()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            return self.client.get_hrv_data(date) or {}
        except AttributeError:
            logger.debug("HRV API not available")
            return {}
        except Exception as e:
            logger.debug(f"HRV data not available: {e}")
            return {}
    
    def get_all_day_stress(self, date: Optional[str] = None) -> List[Dict]:
        """
        Get all-day stress measurements (every few minutes).
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            List of stress readings throughout the day
        """
        self._ensure_authenticated()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            return self.client.get_all_day_stress(date) or []
        except AttributeError:
            logger.debug("All-day stress API not available")
            return []
        except Exception as e:
            logger.debug(f"All-day stress not available: {e}")
            return []

    
    def format_data_for_context(self, data_type: str = "summary", activity_limit: int = 5) -> str:
        """
        Format Garmin data into a readable string for LLM context.
        
        Args:
            data_type: Type of data to format
                      Options: "summary", "activities", "steps", "sleep", "all",
                               "body_battery", "stress", "nutrition", "floors", 
                               "intensity", "spo2", "hrv", "training", "comprehensive"
            activity_limit: Number of activities to include (default: 5, max recommended: 20)
            
        Returns:
            Formatted string containing the requested data
            
        Note:
            - Increase activity_limit for queries about longer time periods
            - Keep under 20 activities to avoid token limits in AI context
            - Use "comprehensive" for detailed health metrics (Body Battery, stress, HRV, etc.)
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
            # Get recent activities with configurable limit
            activities = self.get_activities(activity_limit)
            if activities:
                context_parts.append(f"=== Recent Activities (Last {len(activities)}) ===")
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
        
        # Body Battery data
        if data_type in ["body_battery", "comprehensive", "all"]:
            bb_data = self.get_body_battery(today)
            if bb_data and bb_data.get('current'):
                context_parts.append("=== Body Battery ===")
                context_parts.append(f"Current: {bb_data.get('current', 'N/A')}")
                context_parts.append(f"Highest Today: {bb_data.get('highest', 'N/A')}")
                context_parts.append(f"Lowest Today: {bb_data.get('lowest', 'N/A')}")
                context_parts.append(f"Charged: +{bb_data.get('charged', 0)}")
                context_parts.append(f"Drained: -{bb_data.get('drained', 0)}")
                context_parts.append("")
        
        # Stress data
        if data_type in ["stress", "comprehensive", "all"]:
            stress_data = self.get_stress_data(today)
            if stress_data and stress_data.get('average'):
                context_parts.append("=== Stress Levels ===")
                context_parts.append(f"Average: {stress_data.get('average', 'N/A')}/100")
                context_parts.append(f"Max: {stress_data.get('max', 'N/A')}/100")
                context_parts.append(f"Rest Stress: {stress_data.get('rest', 'N/A')}")
                context_parts.append(f"Activity Stress: {stress_data.get('activity', 'N/A')}")
                context_parts.append(f"Low Stress Duration: {stress_data.get('low_duration', 0) / 60:.0f} min")
                context_parts.append(f"High Stress Duration: {stress_data.get('high_duration', 0) / 60:.0f} min")
                context_parts.append("")
        
        # Respiration data
        if data_type in ["respiration", "comprehensive"]:
            resp_data = self.get_respiration_data(today)
            if resp_data and resp_data.get('waking_avg'):
                context_parts.append("=== Respiration ===")
                context_parts.append(f"Waking Average: {resp_data.get('waking_avg', 'N/A')} breaths/min")
                context_parts.append(f"Sleeping Average: {resp_data.get('sleeping_avg', 'N/A')} breaths/min")
                context_parts.append("")
        
        # Hydration data
        if data_type in ["hydration", "nutrition", "comprehensive"]:
            hydration = self.get_hydration_data(today)
            if hydration:
                context_parts.append("=== Hydration ===")
                total_ml = hydration.get('valueInML', 0)
                context_parts.append(f"Water Intake: {total_ml} ml ({total_ml / 236.588:.1f} cups)")
                context_parts.append("")
        
        # Calories/Nutrition data
        if data_type in ["calories", "nutrition", "comprehensive", "all"]:
            # Get basic calorie data
            cal_data = self.get_calories_data(today)
            if cal_data and cal_data.get('total_burned'):
                context_parts.append("=== Calories ===")
                context_parts.append(f"Total Burned: {cal_data.get('total_burned', 'N/A')} kcal")
                context_parts.append(f"Active Burned: {cal_data.get('active_burned', 'N/A')} kcal")
                context_parts.append(f"BMR: {cal_data.get('bmr', 'N/A')} kcal")
                if cal_data.get('consumed'):
                    context_parts.append(f"Consumed: {cal_data.get('consumed', 'N/A')} kcal")
                    context_parts.append(f"Net: {cal_data.get('net', 'N/A')} kcal")
                context_parts.append("")
            
            # Get detailed nutrition data if available
            nutrition_data = self.get_nutrition_summary(today)
            if nutrition_data and nutrition_data.get('calories_consumed'):
                context_parts.append("=== Nutrition Details ===")
                context_parts.append(f"Calories Consumed: {nutrition_data.get('calories_consumed', 0)} kcal")
                if nutrition_data.get('protein_g'):
                    context_parts.append(f"Protein: {nutrition_data.get('protein_g', 0)}g")
                if nutrition_data.get('carbs_g'):
                    context_parts.append(f"Carbs: {nutrition_data.get('carbs_g', 0)}g")
                if nutrition_data.get('fat_g'):
                    context_parts.append(f"Fat: {nutrition_data.get('fat_g', 0)}g")
                if nutrition_data.get('fiber_g'):
                    context_parts.append(f"Fiber: {nutrition_data.get('fiber_g', 0)}g")
                if nutrition_data.get('sugar_g'):
                    context_parts.append(f"Sugar: {nutrition_data.get('sugar_g', 0)}g")
                context_parts.append("")
            
            # Get food log if available
            food_log = self.get_food_log(today)
            if food_log:
                context_parts.append("=== Food Log ===")
                context_parts.append(f"Number of meals logged: {len(food_log)}")
                for i, meal in enumerate(food_log[:5], 1):  # Show up to 5 meals
                    meal_name = meal.get('name', meal.get('foodName', 'Unknown'))
                    meal_calories = meal.get('calories', 0)
                    context_parts.append(f"{i}. {meal_name} - {meal_calories} kcal")
                context_parts.append("")
        
        # Floors data
        if data_type in ["floors", "comprehensive", "all"]:
            floors_data = self.get_floors_data(today)
            if floors_data and floors_data.get('floors_ascended'):
                context_parts.append("=== Floors Climbed ===")
                context_parts.append(f"Ascended: {floors_data.get('floors_ascended', 0)}")
                context_parts.append(f"Descended: {floors_data.get('floors_descended', 0)}")
                context_parts.append(f"Goal: {floors_data.get('floors_ascended_goal', 'N/A')}")
                context_parts.append("")
        
        # Intensity Minutes
        if data_type in ["intensity", "comprehensive", "all"]:
            intensity = self.get_intensity_minutes(today)
            if intensity:
                context_parts.append("=== Intensity Minutes ===")
                context_parts.append(f"Today Moderate: {intensity.get('moderate', 0)} min")
                context_parts.append(f"Today Vigorous: {intensity.get('vigorous', 0)} min")
                context_parts.append(f"Weekly Moderate: {intensity.get('weekly_moderate', 0)} min")
                context_parts.append(f"Weekly Vigorous: {intensity.get('weekly_vigorous', 0)} min")
                context_parts.append(f"Weekly Goal: {intensity.get('weekly_goal', 150)} min")
                context_parts.append("")
        
        # SpO2 data
        if data_type in ["spo2", "comprehensive"]:
            spo2 = self.get_spo2_data(today)
            if spo2:
                context_parts.append("=== Blood Oxygen (SpO2) ===")
                if 'latestSpO2Value' in spo2:
                    context_parts.append(f"Latest: {spo2.get('latestSpO2Value', 'N/A')}%")
                if 'lowestSpO2Value' in spo2:
                    context_parts.append(f"Lowest: {spo2.get('lowestSpO2Value', 'N/A')}%")
                if 'averageSpO2Value' in spo2:
                    context_parts.append(f"Average: {spo2.get('averageSpO2Value', 'N/A')}%")
                context_parts.append("")
        
        # HRV data
        if data_type in ["hrv", "comprehensive"]:
            hrv = self.get_hrv_data(today)
            if hrv:
                context_parts.append("=== Heart Rate Variability ===")
                if 'lastNightAvg' in hrv:
                    context_parts.append(f"Last Night Average: {hrv.get('lastNightAvg', 'N/A')} ms")
                if 'weeklyAvg' in hrv:
                    context_parts.append(f"Weekly Average: {hrv.get('weeklyAvg', 'N/A')} ms")
                context_parts.append("")
        
        # Training metrics
        if data_type in ["training", "comprehensive"]:
            try:
                max_metrics = self.get_max_metrics()
                if max_metrics:
                    context_parts.append("=== Performance Metrics ===")
                    if 'vo2Max' in max_metrics:
                        context_parts.append(f"VO2 Max: {max_metrics.get('vo2Max', 'N/A')}")
                    if 'fitnessAge' in max_metrics:
                        context_parts.append(f"Fitness Age: {max_metrics.get('fitnessAge', 'N/A')}")
                    context_parts.append("")
            except:
                pass
            
            try:
                training = self.get_training_status()
                if training:
                    context_parts.append("=== Training Status ===")
                    if 'trainingLoad' in training:
                        context_parts.append(f"Load: {training.get('trainingLoad', 'N/A')}")
                    if 'loadFocus' in training:
                        context_parts.append(f"Focus: {training.get('loadFocus', 'N/A')}")
                    context_parts.append("")
            except:
                pass
        
        return "\n".join(context_parts) if context_parts else "No data available"