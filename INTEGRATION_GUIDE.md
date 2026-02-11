# Gmail Add-on Integration Guide

## For Developers: Adding the Email Threat Detection Add-on

This guide explains how to integrate the email threat detection add-on into your application or system for multiple users.

## Table of Contents

1. [Basic Integration](#basic-integration)
2. [Multi-User Setup](#multi-user-setup)
3. [Real-Time Monitoring](#real-time-monitoring)
4. [Custom Workflows](#custom-workflows)
5. [Production Deployment](#production-deployment)

---

## Basic Integration

### Step 1: Import the Add-on

```python
from gmail_addon_integration import GmailAddonIntegration

# Initialize once in your application
addon = GmailAddonIntegration()
```

### Step 2: Create User Profiles

When a new user signs up or enables the feature:

```python
def enable_email_protection_for_user(username, email_address):
    """Enable email threat detection for a user."""
    success = addon.setup_user_profile(
        username=username,
        email=email_address,
        threat_threshold=0.6,  # 60% default
        auto_flag=True
    )
    
    if success:
        print(f"✓ Email protection enabled for {username}")
        return True
    else:
        print(f"✗ Failed to enable protection for {username}")
        return False
```

### Step 3: Analyze Incoming Emails

When a user receives an email:

```python
def check_incoming_email(username, email_data):
    """Check if an incoming email is a threat."""
    
    # Analyze the email
    result = addon.analyze_single_email(username, email_data)
    
    # Take action based on result
    if result['is_threat']:
        # Flag the email
        print(f"⚠️ Threat detected: {result['threat_type']}")
        print(f"Score: {result['threat_score']:.2%}")
        
        # Optional: Move to spam, notify user, etc.
        handle_threat(username, email_data, result)
    else:
        # Email is safe
        print(f"✓ Email appears legitimate")
    
    return result
```

---

## Multi-User Setup

### Bulk User Registration

If you're adding the add-on to existing users:

```python
def bulk_enable_addon(user_list):
    """
    Enable add-on for multiple users.
    
    Args:
        user_list: List of (username, email) tuples
    """
    success_count = 0
    failed_users = []
    
    for username, email in user_list:
        try:
            # Customize settings per user type if needed
            threshold = 0.6  # Default
            
            # Example: Different thresholds for different user types
            if is_executive_user(username):
                threshold = 0.8  # Less sensitive
            elif is_security_user(username):
                threshold = 0.4  # More sensitive
            
            success = addon.setup_user_profile(
                username=username,
                email=email,
                threat_threshold=threshold,
                auto_flag=True
            )
            
            if success:
                success_count += 1
            else:
                failed_users.append(username)
                
        except Exception as e:
            print(f"Error setting up {username}: {e}")
            failed_users.append(username)
    
    print(f"✓ Successfully enabled for {success_count} users")
    if failed_users:
        print(f"✗ Failed for: {', '.join(failed_users)}")
    
    return success_count, failed_users
```

### Per-User Configuration

Allow users to customize their settings:

```python
def update_user_preferences(username, preferences):
    """Update user's add-on preferences."""
    
    # Extract preferences
    sensitivity = preferences.get('sensitivity', 'medium')
    auto_action = preferences.get('auto_action', True)
    
    # Convert sensitivity to threshold
    threshold_map = {
        'low': 0.8,      # Less sensitive
        'medium': 0.6,   # Balanced
        'high': 0.4,     # More sensitive
        'paranoid': 0.3  # Very sensitive
    }
    
    threshold = threshold_map.get(sensitivity, 0.6)
    
    # Update settings
    return addon.update_addon_settings(
        username,
        threat_threshold=threshold,
        auto_flag=auto_action,
        notifications=preferences.get('notifications', True)
    )
```

---

## Real-Time Monitoring

### Continuous Inbox Monitoring

Set up periodic scanning for all users:

```python
import schedule
import time

def scan_all_user_inboxes():
    """Scan all user inboxes for threats."""
    users = addon.list_all_profiles()
    
    results = {}
    for username in users:
        try:
            scan_result = addon.scan_inbox(username, auto_flag=True)
            results[username] = scan_result
            
            # Log or alert if threats found
            if scan_result['threats_found'] > 0:
                notify_user_of_threats(username, scan_result)
                
        except Exception as e:
            print(f"Error scanning {username}: {e}")
    
    return results

# Schedule scanning every 15 minutes
schedule.every(15).minutes.do(scan_all_user_inboxes)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Real-Time Email Hook

Integrate with email reception:

```python
def on_email_received(username, email_data):
    """
    Called when a user receives an email.
    Integrate this with your email system's webhook/callback.
    """
    
    # Analyze immediately
    result = addon.analyze_single_email(username, email_data)
    
    # Take action based on threat level
    if result['threat_score'] >= 0.9:
        # Critical threat - move to spam immediately
        move_to_spam(username, email_data)
        send_notification(username, "Critical threat blocked", result)
        
    elif result['threat_score'] >= 0.7:
        # High threat - flag and warn
        flag_email(username, email_data, result)
        send_warning(username, "Suspicious email detected", result)
        
    elif result['threat_score'] >= 0.5:
        # Medium threat - just flag
        flag_email(username, email_data, result)
    
    # Log for analytics
    log_analysis(username, email_data, result)
    
    return result
```

---

## Custom Workflows

### Workflow 1: User-Controlled Whitelist/Blacklist

```python
class EmailProtectionService:
    """Service class for managing email protection."""
    
    def __init__(self):
        self.addon = GmailAddonIntegration()
    
    def mark_sender_as_safe(self, username, sender_email):
        """User marks a sender as safe (whitelist)."""
        success = self.addon.add_to_whitelist(username, sender_email)
        if success:
            print(f"✓ {sender_email} added to {username}'s trusted senders")
        return success
    
    def mark_sender_as_spam(self, username, sender_email):
        """User marks a sender as spam (blacklist)."""
        success = self.addon.add_to_blacklist(username, sender_email)
        if success:
            print(f"✓ {sender_email} blocked for {username}")
        return success
    
    def report_false_positive(self, username, email_id):
        """User reports a false positive."""
        # Get email details
        # Add sender to whitelist
        # Update statistics
        # Optionally: Use for model retraining
        pass
    
    def report_missed_threat(self, username, email_id):
        """User reports a missed threat."""
        # Get email details
        # Add sender to blacklist
        # Update statistics
        # Optionally: Use for model retraining
        pass
```

### Workflow 2: Team/Organization Protection

```python
class OrganizationEmailProtection:
    """Organization-wide email protection."""
    
    def __init__(self):
        self.addon = GmailAddonIntegration()
        self.org_whitelist = set()
        self.org_blacklist = set()
    
    def add_to_org_whitelist(self, domain_or_email):
        """Add to organization-wide whitelist."""
        self.org_whitelist.add(domain_or_email)
        
        # Apply to all users
        for username in self.addon.list_all_profiles():
            self.addon.add_to_whitelist(username, domain_or_email)
    
    def add_to_org_blacklist(self, domain_or_email):
        """Add to organization-wide blacklist."""
        self.org_blacklist.add(domain_or_email)
        
        # Apply to all users
        for username in self.addon.list_all_profiles():
            self.addon.add_to_blacklist(username, domain_or_email)
    
    def scan_organization(self):
        """Scan all users and generate org-wide report."""
        all_results = {}
        total_threats = 0
        
        for username in self.addon.list_all_profiles():
            result = self.addon.scan_inbox(username)
            all_results[username] = result
            total_threats += result['threats_found']
        
        # Generate organization report
        report = {
            'total_users': len(all_results),
            'total_threats': total_threats,
            'user_results': all_results,
            'top_threats': self._get_top_threats(all_results)
        }
        
        return report
    
    def _get_top_threats(self, results):
        """Extract top threats across organization."""
        # Aggregate and sort threats
        # Return top N
        pass
```

### Workflow 3: Dashboard Integration

```python
def get_user_protection_dashboard(username):
    """Generate dashboard data for frontend."""
    
    dashboard = addon.get_user_dashboard(username)
    
    # Format for frontend
    return {
        'user': {
            'username': dashboard['username'],
            'email': dashboard['email'],
        },
        'settings': {
            'enabled': dashboard['addon_enabled'],
            'sensitivity': _threshold_to_level(dashboard['threat_threshold']),
            'auto_protect': dashboard.get('auto_flag', True)
        },
        'stats': {
            'inbox_count': dashboard['inbox_count'],
            'flagged_count': dashboard['flagged_count'],
            'total_scanned': dashboard['statistics']['total_emails_scanned'],
            'threats_detected': dashboard['statistics']['threats_detected'],
            'last_scan': dashboard['statistics'].get('last_scan')
        },
        'lists': {
            'whitelisted': dashboard['whitelist_count'],
            'blacklisted': dashboard['blacklist_count']
        }
    }

def _threshold_to_level(threshold):
    """Convert threshold to user-friendly level."""
    if threshold <= 0.3:
        return 'Very High'
    elif threshold <= 0.5:
        return 'High'
    elif threshold <= 0.7:
        return 'Medium'
    else:
        return 'Low'
```

---

## Production Deployment

### 1. Database Integration

Store profiles in your database instead of files:

```python
class DatabaseGmailAddonManager(GmailAddonManager):
    """Database-backed addon manager."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        # Override file-based methods with DB methods
    
    def _load_profiles(self):
        """Load profiles from database."""
        query = "SELECT * FROM email_addon_profiles"
        return self.db.execute(query).fetchall()
    
    def _save_profile(self, username):
        """Save profile to database."""
        profile = self.profiles[username]
        query = """
            INSERT INTO email_addon_profiles (username, config, stats)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                config = excluded.config,
                stats = excluded.stats
        """
        self.db.execute(query, (username, profile['addon_config'], 
                               profile['statistics']))
```

### 2. Async Processing

Use async for better performance:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def scan_inbox_async(username):
    """Async inbox scanning."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor,
            addon.scan_inbox,
            username
        )
    return result

async def scan_multiple_users_async(usernames):
    """Scan multiple users concurrently."""
    tasks = [scan_inbox_async(username) for username in usernames]
    results = await asyncio.gather(*tasks)
    return dict(zip(usernames, results))
```

### 3. Monitoring and Logging

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_addon.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('email_addon')

def monitored_scan(username):
    """Scan with logging and monitoring."""
    logger.info(f"Starting scan for user: {username}")
    
    try:
        result = addon.scan_inbox(username)
        
        logger.info(f"Scan complete for {username}: "
                   f"{result['threats_found']} threats found")
        
        # Send metrics to monitoring system
        send_metrics({
            'user': username,
            'threats': result['threats_found'],
            'scanned': result['total_scanned']
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Error scanning {username}: {e}", exc_info=True)
        raise
```

### 4. API Endpoint Example (Flask)

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
addon = GmailAddonIntegration()

@app.route('/api/user/<username>/enable', methods=['POST'])
def enable_protection(username):
    """Enable protection for a user."""
    data = request.json
    success = addon.setup_user_profile(
        username=username,
        email=data['email'],
        threat_threshold=data.get('threshold', 0.6),
        auto_flag=data.get('auto_flag', True)
    )
    return jsonify({'success': success})

@app.route('/api/user/<username>/scan', methods=['POST'])
def scan_inbox(username):
    """Scan user's inbox."""
    result = addon.scan_inbox(username)
    return jsonify(result)

@app.route('/api/user/<username>/analyze', methods=['POST'])
def analyze_email(username):
    """Analyze a single email."""
    email_data = request.json
    result = addon.analyze_single_email(username, email_data)
    return jsonify(result)

@app.route('/api/user/<username>/dashboard', methods=['GET'])
def get_dashboard(username):
    """Get user dashboard."""
    dashboard = addon.get_user_dashboard(username)
    return jsonify(dashboard)
```

---

## Best Practices

1. **Profile Setup:**
   - Create profiles when users opt-in
   - Provide clear UI for threat threshold selection
   - Allow easy whitelist/blacklist management

2. **Performance:**
   - Use async processing for bulk operations
   - Cache user profiles in memory
   - Batch process when possible

3. **User Experience:**
   - Show clear explanations for flagged emails
   - Allow users to report false positives
   - Provide detailed threat analysis on request

4. **Security:**
   - Encrypt sensitive profile data
   - Use secure storage for user lists
   - Log all actions for audit trail

5. **Maintenance:**
   - Regularly retrain models with new data
   - Monitor false positive rates
   - Update detection rules based on new threats

---

## Testing

Test the integration thoroughly:

```python
def test_addon_integration():
    """Test suite for add-on integration."""
    
    # Test 1: User setup
    assert addon.setup_user_profile('test_user', 'test@example.com')
    
    # Test 2: Add sample data
    addon.add_sample_emails('test_user', count=10, phishing_ratio=0.5)
    
    # Test 3: Scan inbox
    result = addon.scan_inbox('test_user')
    assert result['total_scanned'] == 10
    assert result['threats_found'] > 0
    
    # Test 4: Single analysis
    phishing_email = {
        'sender': 'phishing@test.com',
        'subject': 'URGENT!!!',
        'body': 'Click here now! Verify your account immediately!',
        'urls': ['http://malicious.com']
    }
    analysis = addon.analyze_single_email('test_user', phishing_email)
    assert analysis['is_threat'] == True
    
    # Test 5: Whitelist
    addon.add_to_whitelist('test_user', 'safe@test.com')
    safe_email = {
        'sender': 'safe@test.com',
        'subject': 'Test',
        'body': 'Even suspicious content',
        'urls': []
    }
    analysis = addon.analyze_single_email('test_user', safe_email)
    assert analysis['is_threat'] == False
    
    # Cleanup
    addon.remove_user_profile('test_user')
    
    print("✓ All tests passed!")

if __name__ == '__main__':
    test_addon_integration()
```

---

## Support

For integration help, see:
- `demo_gmail_addon.py` - Complete working examples
- `GMAIL_ADDON_SETUP.md` - User-facing documentation
- Module docstrings - API reference
