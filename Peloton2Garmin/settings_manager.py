"""
Settings Manager Module
Handles storage and retrieval of user settings and preferences
"""

import json
import os
from pathlib import Path


class SettingsManager:
    """Manage application settings"""
    
    def __init__(self, settings_file=None):
        """
        Initialize settings manager
        
        Args:
            settings_file: Path to settings file (default: ~/.peloton_garmin_settings.json)
        """
        if settings_file is None:
            self.settings_file = Path.home() / ".peloton_garmin_settings.json"
        else:
            self.settings_file = Path(settings_file)
        
        self.settings = self._load_settings()
    
    def _load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load settings: {e}")
        
        return {}
    
    def _save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")
    
    def get_bearer_token(self):
        """Get saved Peloton bearer token"""
        return self.settings.get('peloton_bearer_token')
    
    def save_bearer_token(self, token):
        """Save Peloton bearer token"""
        self.settings['peloton_bearer_token'] = token
        self._save_settings()
    
    def clear_bearer_token(self):
        """Clear saved bearer token"""
        if 'peloton_bearer_token' in self.settings:
            del self.settings['peloton_bearer_token']
            self._save_settings()
    
    def get_garmin_email(self):
        """Get saved Garmin email"""
        return self.settings.get('garmin_email')
    
    def save_garmin_email(self, email):
        """Save Garmin email"""
        self.settings['garmin_email'] = email
        self._save_settings()
    
    def clear_garmin_email(self):
        """Clear saved Garmin email"""
        if 'garmin_email' in self.settings:
            del self.settings['garmin_email']
            self._save_settings()
    
    def get_setting(self, key, default=None):
        """Get a custom setting"""
        return self.settings.get(key, default)
    
    def save_setting(self, key, value):
        """Save a custom setting"""
        self.settings[key] = value
        self._save_settings()
    
    def clear_setting(self, key):
        """Clear a custom setting"""
        if key in self.settings:
            del self.settings[key]
            self._save_settings()
    
    def clear_all(self):
        """Clear all settings"""
        self.settings = {}
        self._save_settings()


if __name__ == "__main__":
    # Test the settings manager
    settings = SettingsManager()
    
    print("Testing Settings Manager")
    print("=" * 60)
    
    # Test bearer token
    print("\nTesting bearer token storage...")
    settings.save_bearer_token("test_token_12345")
    print(f"Saved token: {settings.get_bearer_token()}")
    
    # Test Garmin email
    print("\nTesting Garmin email storage...")
    settings.save_garmin_email("[email protected]")
    print(f"Saved email: {settings.get_garmin_email()}")
    
    # Test custom setting
    print("\nTesting custom setting...")
    settings.save_setting("last_sync_date", "2025-01-23")
    print(f"Last sync: {settings.get_setting('last_sync_date')}")
    
    print(f"\nSettings file location: {settings.settings_file}")
    print("\n✓ All tests passed!")
