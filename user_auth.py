"""
User Authentication System
Handles user registration, login, and session management.
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path

from supabase_client import supabase

def sign_up(email, password):
    return supabase.auth.sign_up({
        "email": email,
        "password": password
    })

def sign_in(email, password):
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

def sign_out():
    return supabase.auth.sign_out()



class UserAuth:
    """Simple file-based user authentication system."""
    
    def __init__(self, users_file='users.json', sessions_file='sessions.json'):
        self.users_file = Path(users_file)
        self.sessions_file = Path(sessions_file)
        self.users = self._load_users()
        self.sessions = self._load_sessions()
    
    def _load_users(self):
        """Load users from file."""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _load_sessions(self):
        """Load session history from file."""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_sessions(self):
        """Save sessions to file."""
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def _hash_password(self, password):
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password, email=""):
        """Register a new user."""
        if username in self.users:
            return False, "Username already exists"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        self.users[username] = {
            'password_hash': self._hash_password(password),
            'email': email,
            'created_at': datetime.now().isoformat(),
            'total_uploads': 0,
            'total_emails_analyzed': 0
        }
        
        self.sessions[username] = []
        self._save_users()
        self._save_sessions()
        return True, "Registration successful"
    
    def login(self, username, password):
        """Authenticate user."""
        if username not in self.users:
            return False, "Username not found"
        
        password_hash = self._hash_password(password)
        if self.users[username]['password_hash'] != password_hash:
            return False, "Incorrect password"
        
        return True, "Login successful"
    
    def add_session(self, username, session_data):
        """Add a new analysis session."""
        if username not in self.sessions:
            self.sessions[username] = []
        
        session = {
            'timestamp': datetime.now().isoformat(),
            'total_emails': session_data.get('total_emails', 0),
            'phishing_count': session_data.get('phishing_count', 0),
            'legitimate_count': session_data.get('legitimate_count', 0),
            'model_used': session_data.get('model_used', 'Unknown'),
            'csv_filename': session_data.get('csv_filename', 'Unknown')
        }
        
        self.sessions[username].append(session)
        
        # Update user stats
        if username in self.users:
            self.users[username]['total_uploads'] += 1
            self.users[username]['total_emails_analyzed'] += session_data.get('total_emails', 0)
        
        self._save_sessions()
        self._save_users()
    
    def get_user_stats(self, username):
        """Get user statistics."""
        if username not in self.users:
            return None
        
        return {
            'username': username,
            'email': self.users[username].get('email', ''),
            'created_at': self.users[username].get('created_at', ''),
            'total_uploads': self.users[username].get('total_uploads', 0),
            'total_emails_analyzed': self.users[username].get('total_emails_analyzed', 0),
            'sessions': self.sessions.get(username, [])
        }
    
    def get_session_history(self, username):
        """Get all sessions for a user."""
        return self.sessions.get(username, [])

