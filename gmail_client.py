"""
Gmail API Client for MailThreat Analyzer
Handles Gmail OAuth and email fetching
"""

import os
import json
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
from email.mime.text import MIMEText
from datetime import datetime

class GmailClient:
    """Gmail API client for fetching and analyzing emails."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    def __init__(self, credentials_file='gmail_config.json'):
        """Initialize Gmail client."""
        self.credentials_file = credentials_file
        self.creds = None
        self.service = None
        self.user_email = None
    
    def get_authorization_url(self, redirect_uri='http://localhost:5001/api/auth/google/callback', state=None):
        """
        Get OAuth authorization URL for user to visit.
        If state is provided (e.g. "link:CODE"), it is used so the callback can identify link-vs-login flow.
        Returns:
            tuple: (authorization_url, state)
        """
        # Load client configuration
        with open(self.credentials_file, 'r') as f:
            config = json.load(f)
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": config['client_id'],
                    "client_secret": config['client_secret'],
                    "redirect_uris": [redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        kwargs = dict(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        if state is not None:
            kwargs['state'] = state
        authorization_url, state = flow.authorization_url(**kwargs)
        return authorization_url, state
    
    def handle_oauth_callback(self, authorization_response, state, redirect_uri='http://localhost:5001/api/auth/google/callback'):
        """
        Handle OAuth callback and get credentials.
        
        Args:
            authorization_response: Full callback URL with code
            state: State from authorization URL
            
        Returns:
            dict: User info and credentials
        """
        with open(self.credentials_file, 'r') as f:
            config = json.load(f)
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": config['client_id'],
                    "client_secret": config['client_secret'],
                    "redirect_uris": [redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=self.SCOPES,
            state=state,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(authorization_response=authorization_response)
        self.creds = flow.credentials
        
        # Get user info
        user_info = self._get_user_info()
        
        return {
            'email': user_info['email'],
            'name': user_info.get('name', ''),
            'picture': user_info.get('picture', ''),
            'refresh_token': self.creds.refresh_token,
            'access_token': self.creds.token
        }
    
    def authenticate_with_token(self, refresh_token):
        """Authenticate using stored refresh token."""
        with open(self.credentials_file, 'r') as f:
            config = json.load(f)
        
        self.creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            scopes=self.SCOPES
        )
        
        # Refresh the token
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
        
        self.service = build('gmail', 'v1', credentials=self.creds)
        user_info = self._get_user_info()
        self.user_email = user_info['email']
    
    def _get_user_info(self):
        """Get user profile information."""
        service = build('oauth2', 'v2', credentials=self.creds)
        user_info = service.userinfo().get().execute()
        return user_info
    
    def get_messages(self, max_results=100, query='in:inbox'):
        """
        Fetch messages from Gmail.
        
        Args:
            max_results: Maximum number of messages to fetch
            query: Gmail search query (default 'in:inbox' to get inbox mail)
            
        Returns:
            list: List of message objects
        """
        if not self.service:
            raise Exception("Not authenticated. Call authenticate_with_token first.")
        
        try:
            q = query if query else 'in:inbox'
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=q
            ).execute()
            
            messages = results.get('messages', [])
            print(f"[Gmail] list() returned {len(messages)} message IDs (query={q!r})")
            
            # If inbox is empty, try any recent mail (e.g. Sent, or all)
            if not messages and q == 'in:inbox':
                results = self.service.users().messages().list(
                    userId='me',
                    maxResults=max_results,
                    q=''
                ).execute()
                messages = results.get('messages', [])
                print(f"[Gmail] inbox empty; list() with no query returned {len(messages)} IDs")
            
            # Fetch full message details
            full_messages = []
            for msg in messages:
                full_msg = self.get_message_details(msg['id'])
                if full_msg:
                    full_messages.append(full_msg)
            
            if messages and not full_messages:
                print(f"[Gmail] WARNING: got {len(messages)} IDs but 0 full messages (get_message_details failed for all)")
            print(f"[Gmail] returning {len(full_messages)} messages")
            return full_messages
            
        except Exception as e:
            print(f"[Gmail] Error fetching messages: {e}")
            import traceback
            traceback.print_exc()
            # Re-raise so backend can show "Enable Gmail API" to user
            raise
    
    def get_message_details(self, message_id):
        """
        Get detailed information about a specific message.
        
        Returns:
            dict: Email details formatted for threat analysis
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extract header information
            subject = self._get_header(headers, 'Subject')
            sender = self._get_header(headers, 'From')
            to = self._get_header(headers, 'To')
            date = self._get_header(headers, 'Date')
            
            # Extract body
            body = self._get_body(message['payload'])
            
            # Extract sender name and email
            sender_name = ''
            sender_email = sender
            if '<' in sender and '>' in sender:
                sender_name = sender.split('<')[0].strip()
                sender_email = sender.split('<')[1].split('>')[0].strip()
            
            return {
                'id': message_id,
                'gmail_message_id': message_id,
                'subject': subject or '(No Subject)',
                'sender': sender_email,
                'sender_name': sender_name,
                'recipient': to,
                'body': body,
                'received_at': self._parse_date(date),
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', []),
                'thread_id': message.get('threadId', '')
            }
            
        except Exception as e:
            print(f"Error getting message {message_id}: {e}")
            return None
    
    def _get_header(self, headers, name):
        """Extract header value by name."""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _get_body(self, payload):
        """Extract email body from payload."""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data and not body:  # Use HTML only if no plain text
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            data = payload['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body
    
    def _parse_date(self, date_str):
        """Parse email date to ISO format."""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            return datetime.now().isoformat()
    
    def add_label(self, message_id, label_name):
        """Add a label to a message."""
        try:
            # Get or create label
            label_id = self._get_or_create_label(label_name)
            
            # Add label to message
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error adding label: {e}")
            return False
    
    def _get_or_create_label(self, label_name):
        """Get label ID or create if doesn't exist."""
        try:
            # List existing labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Check if label exists
            for label in labels:
                if label['name'] == label_name:
                    return label['id']
            
            # Create new label
            label = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created = self.service.users().labels().create(
                userId='me',
                body=label
            ).execute()
            
            return created['id']
            
        except Exception as e:
            print(f"Error with label: {e}")
            return None
    
    def move_to_trash(self, message_id):
        """Move message to trash."""
        try:
            self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error moving to trash: {e}")
            return False
    
    def get_history(self, start_history_id):
        """
        Get message history for incremental sync.
        
        Args:
            start_history_id: History ID to start from
            
        Returns:
            dict: History data including new messages
        """
        try:
            results = self.service.users().history().list(
                userId='me',
                startHistoryId=start_history_id,
                historyTypes=['messageAdded']
            ).execute()
            
            return results
        except Exception as e:
            print(f"Error getting history: {e}")
            return None


# Helper functions for easy use

def get_gmail_auth_url():
    """Get Gmail OAuth URL for user to visit."""
    client = GmailClient()
    return client.get_authorization_url()

def complete_gmail_auth(authorization_response, state):
    """Complete Gmail OAuth and return user info with tokens."""
    client = GmailClient()
    return client.handle_oauth_callback(authorization_response, state)

def scan_gmail_inbox(refresh_token, max_emails=100):
    """
    Scan a Gmail inbox with stored refresh token.
    
    Returns:
        list: Email messages ready for threat analysis
    """
    client = GmailClient()
    client.authenticate_with_token(refresh_token)
    return client.get_messages(max_results=max_emails)
