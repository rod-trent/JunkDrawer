"""
Peloton Authentication Module
Handles authentication with Peloton API using both Selenium and bearer token methods
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


class PelotonAuthenticator:
    """Handle Peloton authentication"""
    
    def __init__(self):
        self.session = None
        self.user_id = None
        self.base_url = "https://api.onepeloton.com"
    
    def login_with_token(self, bearer_token):
        """
        Login using bearer token from browser
        
        Args:
            bearer_token: The bearer token from browser DevTools
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create session with bearer token
            self.session = requests.Session()
            self.session.headers.update({
                'Authorization': f'Bearer {bearer_token}',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Test the token by getting user info
            response = self.session.get(f"{self.base_url}/api/me")
            
            if response.status_code == 200:
                user_data = response.json()
                self.user_id = user_data.get('id')
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Token login error: {e}")
            return False
    
    def login_with_selenium(self, email, password):
        """
        Login using Selenium browser automation
        
        Args:
            email: Peloton email/username
            password: Peloton password
            
        Returns:
            bool: True if successful, False otherwise
        """
        driver = None
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Start browser
            driver = webdriver.Chrome(options=chrome_options)
            driver.maximize_window()
            wait = WebDriverWait(driver, 30)
            
            # Navigate to Peloton login
            driver.get("https://members.onepeloton.com/login")
            time.sleep(2)
            
            # Find and fill username
            username_field = wait.until(
                EC.presence_of_element_located((By.NAME, "usernameOrEmail"))
            )
            username_field.clear()
            username_field.send_keys(email)
            
            # Find and fill password
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_btn.click()
            
            # Wait for redirect to dashboard
            wait.until(
                lambda d: "members.onepeloton.com" in d.current_url and "login" not in d.current_url
            )
            
            time.sleep(2)
            
            # Extract cookies and create session
            cookies = driver.get_cookies()
            
            self.session = requests.Session()
            for cookie in cookies:
                self.session.cookies.set(
                    cookie['name'],
                    cookie['value'],
                    domain=cookie.get('domain', '.onepeloton.com'),
                    path=cookie.get('path', '/')
                )
            
            # Set headers
            self.session.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Get user info
            response = self.session.get(f"{self.base_url}/api/me")
            if response.status_code == 200:
                user_data = response.json()
                self.user_id = user_data.get('id')
                driver.quit()
                return True
            else:
                driver.quit()
                return False
            
        except Exception as e:
            print(f"Selenium login error: {e}")
            if driver:
                driver.quit()
            return False
    
    def get_recent_workouts(self, limit=50):
        """
        Get recent workouts from Peloton
        
        Args:
            limit: Maximum number of workouts to fetch
            
        Returns:
            list: List of workout dictionaries
        """
        if not self.session or not self.user_id:
            raise Exception("Not logged in. Call login_with_token or login_with_selenium first.")
        
        try:
            url = f"{self.base_url}/api/user/{self.user_id}/workouts"
            params = {
                'limit': limit,
                'page': 0
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                raise Exception(f"Failed to fetch workouts: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Error fetching workouts: {str(e)}")
    
    def get_workout_details(self, workout_id):
        """
        Get detailed information about a specific workout
        
        Args:
            workout_id: The workout ID
            
        Returns:
            dict: Workout details
        """
        if not self.session:
            raise Exception("Not logged in")
        
        try:
            url = f"{self.base_url}/api/workout/{workout_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to fetch workout details: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Error fetching workout details: {str(e)}")
    
    def get_workout_performance_graph(self, workout_id):
        """
        Get performance metrics (heart rate, cadence, output) for a workout
        
        Args:
            workout_id: The workout ID
            
        Returns:
            dict: Performance metrics with time series data
        """
        if not self.session:
            raise Exception("Not logged in")
        
        try:
            url = f"{self.base_url}/api/workout/{workout_id}/performance_graph"
            params = {
                'every_n': 1  # Get every data point
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Warning: Could not fetch performance graph: {e}")
            return None


def test_authentication():
    """Test the authentication methods"""
    
    print("="*60)
    print("Peloton Authentication Test")
    print("="*60)
    
    print("\nChoose authentication method:")
    print("1. Bearer Token (Recommended)")
    print("2. Browser Login (Selenium)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    auth = PelotonAuthenticator()
    
    if choice == "1":
        print("\nBearer Token Login")
        print("-" * 60)
        token = input("Enter bearer token: ").strip()
        
        print("\nAuthenticating...")
        if auth.login_with_token(token):
            print("✓ Successfully authenticated!")
            print(f"User ID: {auth.user_id}")
            
            # Test fetching workouts
            print("\nFetching recent workouts...")
            workouts = auth.get_recent_workouts(limit=5)
            print(f"✓ Found {len(workouts)} recent workouts")
            
            if workouts:
                print("\nMost recent workout:")
                w = workouts[0]
                print(f"  - {w.get('ride', {}).get('title', 'Unknown')}")
                print(f"  - Instructor: {w.get('ride', {}).get('instructor', {}).get('name', 'Unknown')}")
                print(f"  - Date: {w.get('created_at')}")
        else:
            print("✗ Authentication failed")
    
    elif choice == "2":
        print("\nBrowser Login (Selenium)")
        print("-" * 60)
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()
        
        print("\nOpening browser...")
        if auth.login_with_selenium(email, password):
            print("✓ Successfully authenticated!")
            print(f"User ID: {auth.user_id}")
            
            # Test fetching workouts
            print("\nFetching recent workouts...")
            workouts = auth.get_recent_workouts(limit=5)
            print(f"✓ Found {len(workouts)} recent workouts")
        else:
            print("✗ Authentication failed")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    test_authentication()
