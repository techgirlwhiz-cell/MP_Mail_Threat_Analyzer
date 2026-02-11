"""
Gmail Add-on Manager
Manages modular email threat detection add-ons for multiple user profiles.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class GmailAddonManager:
    """Manages email threat detection add-ons for multiple user profiles."""
    
    def __init__(self, config_dir: str = 'user_profiles'):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.profiles = self._load_profiles()
    
    def _load_profiles(self) -> Dict:
        """Load all user profiles."""
        profiles = {}
        if self.config_dir.exists():
            for profile_file in self.config_dir.glob('*.json'):
                try:
                    with open(profile_file, 'r') as f:
                        profile_data = json.load(f)
                        username = profile_file.stem
                        profiles[username] = profile_data
                except Exception as e:
                    print(f"Error loading profile {profile_file}: {e}")
        return profiles
    
    def create_profile(self, username: str, email: str, 
                      threat_threshold: float = 0.5,
                      enable_auto_flag: bool = True,
                      enable_notifications: bool = True) -> bool:
        """
        Create a new user profile with add-on configuration.
        
        Args:
            username: User's unique identifier
            email: User's email address
            threat_threshold: Threshold for flagging threats (0.0 to 1.0)
            enable_auto_flag: Whether to automatically flag threats
            enable_notifications: Whether to send notifications
            
        Returns:
            True if profile created successfully, False otherwise
        """
        if username in self.profiles:
            print(f"Profile for {username} already exists.")
            return False
        
        profile = {
            'username': username,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'addon_config': {
                'enabled': True,
                'threat_threshold': threat_threshold,
                'auto_flag': enable_auto_flag,
                'notifications': enable_notifications,
                'model_version': '1.0',
                'whitelist': [],
                'blacklist': []
            },
            'statistics': {
                'total_emails_scanned': 0,
                'threats_detected': 0,
                'false_positives': 0,
                'last_scan': None
            }
        }
        
        # Save profile
        profile_path = self.config_dir / f"{username}.json"
        with open(profile_path, 'w') as f:
            json.dump(profile, f, indent=2)
        
        self.profiles[username] = profile
        print(f"✓ Profile created for {username}")
        return True
    
    def update_profile_config(self, username: str, **kwargs) -> bool:
        """
        Update user profile configuration.
        
        Args:
            username: User's identifier
            **kwargs: Configuration parameters to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        if username not in self.profiles:
            print(f"Profile for {username} not found.")
            return False
        
        # Update addon configuration
        for key, value in kwargs.items():
            if key in self.profiles[username]['addon_config']:
                self.profiles[username]['addon_config'][key] = value
        
        # Save updated profile
        profile_path = self.config_dir / f"{username}.json"
        with open(profile_path, 'w') as f:
            json.dump(self.profiles[username], f, indent=2)
        
        print(f"✓ Profile updated for {username}")
        return True
    
    def add_to_whitelist(self, username: str, sender_email: str) -> bool:
        """Add an email to the user's whitelist."""
        if username not in self.profiles:
            return False
        
        whitelist = self.profiles[username]['addon_config']['whitelist']
        if sender_email not in whitelist:
            whitelist.append(sender_email)
            self._save_profile(username)
        return True
    
    def add_to_blacklist(self, username: str, sender_email: str) -> bool:
        """Add an email to the user's blacklist."""
        if username not in self.profiles:
            return False
        
        blacklist = self.profiles[username]['addon_config']['blacklist']
        if sender_email not in blacklist:
            blacklist.append(sender_email)
            self._save_profile(username)
        return True
    
    def get_profile(self, username: str) -> Optional[Dict]:
        """Get user profile."""
        return self.profiles.get(username)
    
    def update_statistics(self, username: str, scanned: int = 0, 
                         threats: int = 0, false_positives: int = 0):
        """Update user statistics with the last scan results (replaces, does not add)."""
        if username not in self.profiles:
            return
        
        stats = self.profiles[username]['statistics']
        stats['total_emails_scanned'] = scanned   # last scan count only
        stats['threats_detected'] = threats      # last scan count only
        stats['false_positives'] = stats.get('false_positives', 0) + false_positives
        stats['last_scan'] = datetime.now().isoformat()
        
        self._save_profile(username)
    
    def _save_profile(self, username: str):
        """Save a user profile to disk."""
        profile_path = self.config_dir / f"{username}.json"
        with open(profile_path, 'w') as f:
            json.dump(self.profiles[username], f, indent=2)
    
    def list_profiles(self) -> List[str]:
        """List all user profiles."""
        return list(self.profiles.keys())
    
    def delete_profile(self, username: str) -> bool:
        """Delete a user profile."""
        if username not in self.profiles:
            return False
        
        profile_path = self.config_dir / f"{username}.json"
        if profile_path.exists():
            profile_path.unlink()
        
        del self.profiles[username]
        return True
