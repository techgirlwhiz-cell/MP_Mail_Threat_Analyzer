"""
Gmail Add-on Integration
Main integration module that connects the threat detector with Gmail simulator
and manages user profiles.
"""

from typing import Dict, List, Optional
from gmail_addon_manager import GmailAddonManager
from email_threat_detector import EmailThreatDetector
from gmail_simulator import GmailSimulator


class GmailAddonIntegration:
    """
    Main integration class that provides the Gmail add-on functionality.
    This is the primary interface for adding threat detection to user profiles.
    """
    
    def __init__(self):
        self.addon_manager = GmailAddonManager()
        self.threat_detector = EmailThreatDetector()
        self.gmail_simulator = GmailSimulator()
    
    def setup_user_profile(self, username: str, email: str, 
                          threat_threshold: float = 0.6,
                          auto_flag: bool = True) -> bool:
        """
        Set up email threat detection for a user profile.
        
        Args:
            username: Unique username
            email: User's email address
            threat_threshold: Threshold for automatic threat flagging (0.0 to 1.0)
            auto_flag: Whether to automatically flag threats
            
        Returns:
            True if setup successful
        """
        # Create profile in addon manager
        profile_created = self.addon_manager.create_profile(
            username=username,
            email=email,
            threat_threshold=threat_threshold,
            enable_auto_flag=auto_flag,
            enable_notifications=True
        )
        
        if profile_created:
            # Create simulated inbox
            self.gmail_simulator.create_inbox(username, email)
            print(f"✓ Email threat detection add-on enabled for {username}")
            return True
        
        return False
    
    def scan_inbox(self, username: str, auto_flag: bool = None) -> Dict:
        """
        Scan a user's inbox for threats.
        
        Args:
            username: Username to scan inbox for
            auto_flag: Override profile setting for auto-flagging
            
        Returns:
            Dictionary with scan results
        """
        # Get user profile
        profile = self.addon_manager.get_profile(username)
        if not profile:
            return {'error': f'Profile not found for {username}'}
        
        # Get inbox emails
        emails = self.gmail_simulator.get_inbox(username, unread_only=False)
        
        if not emails:
            return {
                'username': username,
                'total_scanned': 0,
                'threats_found': 0,
                'results': []
            }
        
        # Determine auto-flag setting
        if auto_flag is None:
            auto_flag = profile['addon_config']['auto_flag']
        
        threat_threshold = min(profile['addon_config']['threat_threshold'], 0.6)  # cap so threats are caught
        whitelist = profile['addon_config']['whitelist']
        blacklist = profile['addon_config']['blacklist']
        
        # Scan each email
        scan_results = []
        threats_found = 0
        
        for email in emails:
            sender = email.get('sender', '')
            
            # Check whitelist/blacklist
            if sender in whitelist:
                result = {
                    'email_id': email['id'],
                    'sender': sender,
                    'subject': email.get('subject', ''),
                    'is_threat': False,
                    'threat_score': 0.0,
                    'reason': 'Sender is whitelisted'
                }
                scan_results.append(result)
                continue
            
            if sender in blacklist:
                result = {
                    'email_id': email['id'],
                    'sender': sender,
                    'subject': email.get('subject', ''),
                    'is_threat': True,
                    'threat_score': 1.0,
                    'reason': 'Sender is blacklisted'
                }
                
                if auto_flag:
                    self.gmail_simulator.flag_email(username, email['id'], 
                                                   'Blacklisted sender')
                
                threats_found += 1
                scan_results.append(result)
                continue
            
            # Perform threat detection
            analysis = self.threat_detector.analyze_email(email)
            
            is_threat = analysis['threat_score'] >= threat_threshold
            
            if is_threat:
                threats_found += 1
                
                # Auto-flag if enabled
                if auto_flag:
                    flag_reason = f"Threat detected: {analysis['threat_type']} " \
                                f"(confidence: {analysis['confidence']}, " \
                                f"score: {analysis['threat_score']:.2f})"
                    self.gmail_simulator.flag_email(username, email['id'], flag_reason)
            
            result = {
                'email_id': email['id'],
                'sender': sender,
                'subject': email.get('subject', ''),
                'is_threat': is_threat,
                'threat_score': analysis['threat_score'],
                'threat_type': analysis['threat_type'],
                'confidence': analysis['confidence'],
                'risk_factors': analysis['risk_factors'],
                'recommendations': analysis['recommendations']
            }
            
            scan_results.append(result)
        
        # Update statistics
        self.addon_manager.update_statistics(
            username,
            scanned=len(emails),
            threats=threats_found
        )
        
        return {
            'username': username,
            'total_scanned': len(emails),
            'threats_found': threats_found,
            'threat_rate': threats_found / len(emails) if emails else 0,
            'results': scan_results
        }
    
    def analyze_single_email(self, username: str, email_data: Dict) -> Dict:
        """
        Analyze a single email for a user.
        
        Args:
            username: Username
            email_data: Email data to analyze
            
        Returns:
            Analysis results
        """
        profile = self.addon_manager.get_profile(username)
        if not profile:
            return {'error': f'Profile not found for {username}'}
        
        # Check whitelist/blacklist
        sender = email_data.get('sender', '')
        whitelist = profile['addon_config']['whitelist']
        blacklist = profile['addon_config']['blacklist']
        
        if sender in whitelist:
            return {
                'is_threat': False,
                'threat_score': 0.0,
                'reason': 'Sender is whitelisted'
            }
        
        if sender in blacklist:
            return {
                'is_threat': True,
                'threat_score': 1.0,
                'threat_type': 'blacklisted',
                'reason': 'Sender is blacklisted'
            }
        
        # Perform threat detection
        analysis = self.threat_detector.analyze_email(email_data)
        return analysis
    
    def add_sample_emails(self, username: str, count: int = 10, 
                         phishing_ratio: float = 0.3) -> bool:
        """
        Add sample emails to a user's inbox for testing.
        
        Args:
            username: Username
            count: Number of emails to generate
            phishing_ratio: Ratio of phishing emails
            
        Returns:
            True if successful
        """
        try:
            self.gmail_simulator.generate_sample_emails(username, count, phishing_ratio)
            print(f"✓ Added {count} sample emails to {username}'s inbox")
            return True
        except Exception as e:
            print(f"Error adding sample emails: {e}")
            return False
    
    def get_user_dashboard(self, username: str) -> Dict:
        """
        Get dashboard information for a user.
        
        Args:
            username: Username
            
        Returns:
            Dashboard data
        """
        profile = self.addon_manager.get_profile(username)
        if not profile:
            return {'error': f'Profile not found for {username}'}
        
        # Get flagged emails
        flagged = self.gmail_simulator.get_flagged_emails(username)
        
        # Get inbox count
        inbox = self.gmail_simulator.get_inbox(username)
        
        return {
            'username': username,
            'email': profile['email'],
            'addon_enabled': profile['addon_config']['enabled'],
            'threat_threshold': profile['addon_config']['threat_threshold'],
            'auto_flag': profile['addon_config']['auto_flag'],
            'statistics': profile['statistics'],
            'inbox_count': len(inbox),
            'flagged_count': len(flagged),
            'whitelist_count': len(profile['addon_config']['whitelist']),
            'blacklist_count': len(profile['addon_config']['blacklist'])
        }
    
    def update_addon_settings(self, username: str, **settings) -> bool:
        """
        Update add-on settings for a user.
        
        Args:
            username: Username
            **settings: Settings to update (threat_threshold, auto_flag, etc.)
            
        Returns:
            True if successful
        """
        return self.addon_manager.update_profile_config(username, **settings)
    
    def add_to_whitelist(self, username: str, sender_email: str) -> bool:
        """Add sender to whitelist."""
        return self.addon_manager.add_to_whitelist(username, sender_email)
    
    def add_to_blacklist(self, username: str, sender_email: str) -> bool:
        """Add sender to blacklist."""
        return self.addon_manager.add_to_blacklist(username, sender_email)
    
    def list_all_profiles(self) -> List[str]:
        """List all configured user profiles."""
        return self.addon_manager.list_profiles()
    
    def remove_user_profile(self, username: str) -> bool:
        """
        Remove a user profile and disable add-on.
        
        Args:
            username: Username to remove
            
        Returns:
            True if successful
        """
        return self.addon_manager.delete_profile(username)
