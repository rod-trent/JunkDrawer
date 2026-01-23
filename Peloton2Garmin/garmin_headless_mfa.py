"""
Garmin Connect Authentication with Headless MFA Support
Handles MFA code entry directly in the app without browser
"""

import garth
from garth.exc import GarthHTTPError
from pathlib import Path


class GarminAuthenticator:
    """Handle Garmin authentication with headless MFA support"""
    
    def __init__(self, token_store_path=None):
        """
        Initialize authenticator
        
        Args:
            token_store_path: Directory to store tokens (default: ~/.garmin_tokens)
        """
        if token_store_path is None:
            self.token_store = Path.home() / ".garmin_tokens"
        else:
            self.token_store = Path(token_store_path)
        
        self.token_store.mkdir(parents=True, exist_ok=True)
        self.client_state = None
    
    def login_step1(self, email, password):
        """
        Step 1: Submit credentials to Garmin
        
        Returns:
            dict with status:
            - {'success': True, 'client': client} if no MFA needed
            - {'mfa_required': True, 'client_state': state} if MFA needed
            - {'error': 'message'} on failure
        """
        try:
            # Try to resume existing session first
            try:
                garth.resume(str(self.token_store))
                from garminconnect import Garmin
                client = Garmin()
                client.garth = garth
                
                # Verify session
                from datetime import datetime
                client.get_user_summary(datetime.now().strftime('%Y-%m-%d'))
                return {'success': True, 'client': client}
            except:
                pass  # No valid saved session
            
            # Attempt login with return_on_mfa flag
            try:
                # This will return early if MFA is required
                result = garth.login(email, password, return_on_mfa=True)
                
                # If result is a tuple, MFA is required
                if isinstance(result, tuple) and len(result) == 2:
                    oauth1_token, client_state = result
                    # Store client_state for step 2
                    self.client_state = client_state
                    return {'mfa_required': True, 'client_state': client_state}
                
                # Otherwise login succeeded without MFA
                garth.save(str(self.token_store))
                
                from garminconnect import Garmin
                client = Garmin()
                client.garth = garth
                
                return {'success': True, 'client': client}
                
            except GarthHTTPError as e:
                return {'error': f'Login failed: {str(e)}'}
                    
        except Exception as e:
            return {'error': f'Authentication error: {str(e)}'}
    
    def login_step2_submit_mfa(self, mfa_code, client_state=None):
        """
        Step 2: Submit MFA code after step 1 indicated MFA required
        
        Args:
            mfa_code: 6-digit MFA code from user's phone
            client_state: Optional client state from step 1 (uses stored if not provided)
            
        Returns:
            dict with status:
            - {'success': True, 'client': client} on success
            - {'error': 'message'} on failure
        """
        if client_state is None:
            client_state = self.client_state
        
        if not client_state:
            return {'error': 'Must call login_step1 first'}
        
        try:
            # Resume login with MFA code
            garth.resume_login(client_state, mfa_code)
            
            # Save tokens
            garth.save(str(self.token_store))
            
            # Create Garmin client
            from garminconnect import Garmin
            client = Garmin()
            client.garth = garth
            
            return {'success': True, 'client': client}
            
        except Exception as e:
            return {'error': f'MFA submission failed: {str(e)}'}
    
    def login(self, email, password, mfa_callback=None):
        """
        Complete login (convenience method that handles MFA with callback)
        
        Args:
            email: Garmin email
            password: Garmin password
            mfa_callback: Function that returns MFA code when called
            
        Returns:
            Garmin client or None on failure
        """
        # Step 1: Submit credentials
        result = self.login_step1(email, password)
        
        if result.get('success'):
            return result['client']
        
        if result.get('mfa_required'):
            if not mfa_callback:
                raise Exception("MFA required but no callback provided")
            
            # Get MFA code from callback
            mfa_code = mfa_callback()
            if not mfa_code:
                raise Exception("MFA code required but not provided")
            
            # Step 2: Submit MFA
            result = self.login_step2_submit_mfa(mfa_code, result.get('client_state'))
            
            if result.get('success'):
                return result['client']
            else:
                raise Exception(result.get('error', 'MFA submission failed'))
        
        raise Exception(result.get('error', 'Login failed'))


def test_authentication():
    """Test the two-step authentication flow"""
    
    print("="*60)
    print("Garmin Headless MFA Authentication Test")
    print("="*60)
    
    email = input("\nEnter Garmin email: ")
    password = input("Enter Garmin password: ")
    
    auth = GarminAuthenticator()
    
    print("\nStep 1: Submitting credentials to Garmin...")
    result = auth.login_step1(email, password)
    
    if result.get('success'):
        print("✓ Login successful (no MFA required)")
        client = result['client']
        print("✓ Authentication complete!")
        return
    
    if result.get('mfa_required'):
        print("\n" + "="*60)
        print("MFA Required")
        print("="*60)
        print("Garmin has sent a 6-digit code to your phone.")
        mfa_code = input("Enter MFA code: ")
        
        print("\nStep 2: Submitting MFA code...")
        result = auth.login_step2_submit_mfa(mfa_code)
        
        if result.get('success'):
            print("✓ MFA successful!")
            client = result['client']
            print("✓ Authentication complete!")
        else:
            print(f"✗ MFA failed: {result.get('error')}")
    else:
        print(f"✗ Login failed: {result.get('error')}")


if __name__ == "__main__":
    test_authentication()
