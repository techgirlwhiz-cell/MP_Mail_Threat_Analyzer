"""
Gmail Simulator
Simulates Gmail inbox environment for testing the email threat detection add-on.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class GmailSimulator:
    """
    Simulates a Gmail inbox environment for testing threat detection.
    This allows testing the add-on without actual Gmail API integration.
    """
    
    def __init__(self, inbox_dir: str = 'simulated_inboxes'):
        self.inbox_dir = Path(inbox_dir)
        self.inbox_dir.mkdir(exist_ok=True)
        self.user_inboxes = {}
    
    def create_inbox(self, username: str, email: str) -> bool:
        """Create a simulated inbox for a user."""
        inbox_path = self.inbox_dir / f"{username}_inbox.json"
        
        if inbox_path.exists():
            self._load_inbox(username)
            return True
        
        inbox = {
            'username': username,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'emails': [],
            'folders': {
                'inbox': [],
                'flagged': [],
                'spam': [],
                'trash': []
            }
        }
        
        with open(inbox_path, 'w') as f:
            json.dump(inbox, f, indent=2)
        
        self.user_inboxes[username] = inbox
        return True
    
    def _load_inbox(self, username: str):
        """Load a user's inbox from disk."""
        inbox_path = self.inbox_dir / f"{username}_inbox.json"
        if inbox_path.exists():
            with open(inbox_path, 'r') as f:
                self.user_inboxes[username] = json.load(f)
    
    def _save_inbox(self, username: str):
        """Save a user's inbox to disk."""
        inbox_path = self.inbox_dir / f"{username}_inbox.json"
        with open(inbox_path, 'w') as f:
            json.dump(self.user_inboxes[username], f, indent=2)
    
    def add_email(self, username: str, email_data: Dict) -> bool:
        """Add an email to a user's inbox."""
        if username not in self.user_inboxes:
            self._load_inbox(username)
        
        if username not in self.user_inboxes:
            return False
        
        # Add unique ID and timestamp
        email_data['id'] = self._generate_email_id()
        email_data['received_at'] = datetime.now().isoformat()
        email_data['folder'] = 'inbox'
        email_data['is_read'] = False
        email_data['is_flagged'] = False
        
        # Add to inbox
        self.user_inboxes[username]['emails'].append(email_data)
        self.user_inboxes[username]['folders']['inbox'].append(email_data['id'])
        
        self._save_inbox(username)
        return True
    
    def get_inbox(self, username: str, unread_only: bool = False) -> List[Dict]:
        """Get all emails in inbox."""
        if username not in self.user_inboxes:
            self._load_inbox(username)
        
        if username not in self.user_inboxes:
            return []
        
        emails = self.user_inboxes[username]['emails']
        
        if unread_only:
            emails = [e for e in emails if not e.get('is_read', False)]
        
        # Return only inbox emails
        inbox_ids = self.user_inboxes[username]['folders']['inbox']
        return [e for e in emails if e['id'] in inbox_ids]
    
    def flag_email(self, username: str, email_id: str, reason: str = '') -> bool:
        """Flag an email as potential threat."""
        if username not in self.user_inboxes:
            self._load_inbox(username)
        
        if username not in self.user_inboxes:
            return False
        
        # Find email
        for email in self.user_inboxes[username]['emails']:
            if email['id'] == email_id:
                email['is_flagged'] = True
                email['flag_reason'] = reason
                email['flagged_at'] = datetime.now().isoformat()
                
                # Add to flagged folder
                if email_id not in self.user_inboxes[username]['folders']['flagged']:
                    self.user_inboxes[username]['folders']['flagged'].append(email_id)
                
                self._save_inbox(username)
                return True
        
        return False
    
    def move_to_spam(self, username: str, email_id: str) -> bool:
        """Move email to spam folder."""
        if username not in self.user_inboxes:
            self._load_inbox(username)
        
        if username not in self.user_inboxes:
            return False
        
        # Remove from inbox
        inbox = self.user_inboxes[username]['folders']['inbox']
        if email_id in inbox:
            inbox.remove(email_id)
        
        # Add to spam
        spam = self.user_inboxes[username]['folders']['spam']
        if email_id not in spam:
            spam.append(email_id)
        
        # Update email folder
        for email in self.user_inboxes[username]['emails']:
            if email['id'] == email_id:
                email['folder'] = 'spam'
                break
        
        self._save_inbox(username)
        return True
    
    def get_flagged_emails(self, username: str) -> List[Dict]:
        """Get all flagged emails."""
        if username not in self.user_inboxes:
            self._load_inbox(username)
        
        if username not in self.user_inboxes:
            return []
        
        flagged_ids = self.user_inboxes[username]['folders']['flagged']
        return [e for e in self.user_inboxes[username]['emails'] if e['id'] in flagged_ids]
    
    def generate_sample_emails(self, username: str, count: int = 10, 
                              phishing_ratio: float = 0.3) -> List[Dict]:
        """
        Generate sample emails for testing.
        
        Args:
            username: User to add emails to
            count: Number of emails to generate
            phishing_ratio: Ratio of phishing emails (0.0 to 1.0)
        """
        legitimate_samples = [
            {
                'sender': 'newsletter@company.com',
                'sender_name': 'Company Newsletter',
                'subject': 'Weekly Update - January 2026',
                'body': 'Hello, here is your weekly update with the latest news and articles. Check out our blog for more information.',
                'urls': ['https://company.com/blog', 'https://company.com/unsubscribe']
            },
            {
                'sender': 'support@amazon.com',
                'sender_name': 'Amazon',
                'subject': 'Your order has been shipped',
                'body': 'Good news! Your order #12345 has been shipped and will arrive by Jan 28. Track your package at the link below.',
                'urls': ['https://amazon.com/track']
            },
            {
                'sender': 'friend@gmail.com',
                'sender_name': 'John Smith',
                'subject': 'Coffee next week?',
                'body': 'Hey! Want to grab coffee next Tuesday? Let me know if you\'re free. Looking forward to catching up!',
                'urls': []
            },
            {
                'sender': 'hr@yourcompany.com',
                'sender_name': 'HR Department',
                'subject': 'Team Meeting - Thursday 2pm',
                'body': 'Reminder: We have our monthly team meeting this Thursday at 2pm in Conference Room B. See you there!',
                'urls': []
            },
        ]
        
        phishing_samples = [
            {
                'sender': 'security@paypa1-verify.com',
                'sender_name': 'PayPal Security',
                'subject': 'URGENT: Your PayPal Account Has Been Suspended',
                'body': 'Your PayPal account has been suspended due to suspicious activity. Click here immediately to verify your identity and restore access. You have 24 hours before permanent suspension! Click here: http://paypal-verify-2026.tk/login',
                'urls': ['http://paypal-verify-2026.tk/login', 'http://192.168.1.1/verify']
            },
            {
                'sender': 'no-reply@amazon-security.tk',
                'sender_name': 'Amazon Account',
                'subject': 'Verify your account now!',
                'body': 'Dear customer, your Amazon account will be locked in 12 hours if you don\'t verify now! Click here immediately to confirm your identity: http://amazon-verify.tk/confirm PASSWORD EXPIRED! ACT NOW!',
                'urls': ['http://amazon-verify.tk/confirm']
            },
            {
                'sender': 'irs_official_2026@yahoo.com',
                'sender_name': 'IRS Tax Department',
                'subject': 'Tax Refund - Immediate Action Required!!!',
                'body': 'You are eligible for a tax refund of $2,543.00. Click here NOW to claim your refund before it expires! You must act within 24 hours or forfeit your money! URGENT! http://irs-refund-2026.tk',
                'urls': ['http://irs-refund-2026.tk']
            },
            {
                'sender': 'ceo@company-urgent.com',
                'sender_name': 'CEO Office',
                'subject': 'Wire Transfer Needed ASAP',
                'body': 'I need you to process an urgent wire transfer immediately. I\'m in a meeting and can\'t call. Send $5000 to the account below RIGHT NOW. This is confidential and time sensitive!',
                'urls': []
            },
            {
                'sender': 'security567@bank-alert.net',
                'sender_name': 'Bank Security',
                'subject': 'ALERT: Suspicious Activity Detected!!!!',
                'body': 'URGENT SECURITY ALERT! Suspicious login detected on your account from China! VERIFY NOW or your account will be LOCKED PERMANENTLY! Click here: http://193.45.67.89/verify-account PASSWORD RESET REQUIRED!',
                'urls': ['http://193.45.67.89/verify-account']
            },
        ]
        
        generated_emails = []
        phishing_count = int(count * phishing_ratio)
        legitimate_count = count - phishing_count
        
        # Generate emails
        for i in range(legitimate_count):
            email = random.choice(legitimate_samples).copy()
            email['actual_label'] = 'legitimate'
            generated_emails.append(email)
        
        for i in range(phishing_count):
            email = random.choice(phishing_samples).copy()
            email['actual_label'] = 'phishing'
            generated_emails.append(email)
        
        # Shuffle
        random.shuffle(generated_emails)
        
        # Add to inbox
        for email in generated_emails:
            self.add_email(username, email)
        
        return generated_emails
    
    def _generate_email_id(self) -> str:
        """Generate a unique email ID."""
        return f"msg_{random.randint(100000, 999999)}_{int(datetime.now().timestamp())}"
    
    def clear_inbox(self, username: str) -> bool:
        """Clear all emails from inbox."""
        if username not in self.user_inboxes:
            self._load_inbox(username)
        
        if username not in self.user_inboxes:
            return False
        
        self.user_inboxes[username]['emails'] = []
        self.user_inboxes[username]['folders'] = {
            'inbox': [],
            'flagged': [],
            'spam': [],
            'trash': []
        }
        
        self._save_inbox(username)
        return True
