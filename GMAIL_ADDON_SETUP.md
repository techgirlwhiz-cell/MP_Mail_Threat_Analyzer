# Gmail Email Threat Detection Add-on

## Overview

This is a **modular Machine Learning and Natural Language Processing (ML/NLP) system** that provides email threat detection capabilities. The system can be easily integrated as an add-on for multiple user profiles, with each profile having customized settings and independent configuration.

### Key Features

✅ **Multi-User Support** - Each user has their own profile with independent settings  
✅ **ML/NLP Threat Detection** - Advanced machine learning models analyze email content  
✅ **Customizable Thresholds** - Each user can set their own sensitivity level  
✅ **Auto-Flagging** - Automatically flag suspicious emails  
✅ **Whitelist/Blacklist** - Per-user trusted and blocked sender lists  
✅ **Real-Time Analysis** - Analyze emails as they arrive  
✅ **Detailed Reports** - Risk factors, threat scores, and recommendations  
✅ **Statistics Dashboard** - Track detection performance per user  

## Architecture

The system consists of several modular components:

```
gmail_addon_integration.py    # Main integration interface
├── gmail_addon_manager.py     # User profile management
├── email_threat_detector.py   # Core ML/NLP threat detection engine
├── gmail_simulator.py         # Gmail inbox simulation (for testing)
├── email_analyzer.py          # NLP content analysis
└── feature_extractor.py       # Feature extraction
```

## Installation

### 1. Prerequisites

Ensure you have Python 3.8+ installed, then install required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Download NLTK Data

The system will automatically download required NLTK data on first run, but you can manually download it:

```bash
python setup_nltk.py
```

### 3. Train the ML Model (Optional)

If you have training data, train the model:

```bash
python train_model.py
```

The system will use rule-based detection if no trained model is available.

## Quick Start

### Setting Up User Profiles

```python
from gmail_addon_integration import GmailAddonIntegration

# Initialize the add-on system
addon = GmailAddonIntegration()

# Create a user profile
addon.setup_user_profile(
    username='john_doe',
    email='john@example.com',
    threat_threshold=0.6,  # 60% threshold
    auto_flag=True         # Automatically flag threats
)

# Create another profile with different settings
addon.setup_user_profile(
    username='jane_smith',
    email='jane@example.com',
    threat_threshold=0.8,  # 80% threshold (less sensitive)
    auto_flag=False        # Manual review
)
```

### Analyzing Emails

#### Single Email Analysis

```python
# Analyze a single email
email_data = {
    'sender': 'security@paypal-verify.com',
    'sender_name': 'PayPal Security',
    'subject': 'URGENT: Account Suspended',
    'body': 'Your account has been suspended. Click here to verify...',
    'urls': ['http://paypal-verify.tk/login']
}

result = addon.analyze_single_email('john_doe', email_data)

print(f"Threat Score: {result['threat_score']:.2%}")
print(f"Threat Type: {result['threat_type']}")
print(f"Risk Factors: {result['risk_factors']}")
```

#### Batch Inbox Scanning

```python
# Scan entire inbox for threats
scan_results = addon.scan_inbox('john_doe', auto_flag=True)

print(f"Total Scanned: {scan_results['total_scanned']}")
print(f"Threats Found: {scan_results['threats_found']}")
print(f"Threat Rate: {scan_results['threat_rate']:.1%}")

# Review detected threats
for email in scan_results['results']:
    if email['is_threat']:
        print(f"⚠️ {email['subject']} - Score: {email['threat_score']:.2%}")
```

### Managing Whitelists and Blacklists

```python
# Add trusted senders (whitelist)
addon.add_to_whitelist('john_doe', 'newsletter@company.com')
addon.add_to_whitelist('john_doe', 'support@trusted-vendor.com')

# Add blocked senders (blacklist)
addon.add_to_blacklist('john_doe', 'spam@malicious.com')

# These settings are per-user - Jane's whitelist is separate from John's
addon.add_to_whitelist('jane_smith', 'different@trusted.com')
```

### Viewing User Dashboard

```python
# Get user dashboard with statistics
dashboard = addon.get_user_dashboard('john_doe')

print(f"Email: {dashboard['email']}")
print(f"Inbox Count: {dashboard['inbox_count']}")
print(f"Flagged Count: {dashboard['flagged_count']}")
print(f"Total Scanned: {dashboard['statistics']['total_emails_scanned']}")
print(f"Threats Detected: {dashboard['statistics']['threats_detected']}")
```

### Updating Settings

```python
# Update user's threat threshold
addon.update_addon_settings(
    'john_doe',
    threat_threshold=0.5,  # Make more sensitive
    auto_flag=True,
    notifications=True
)
```

## Running the Demo

A comprehensive demonstration script is provided:

```bash
python demo_gmail_addon.py
```

This demo shows:
- Setting up multiple user profiles
- Adding sample emails (legitimate and phishing)
- Scanning inboxes with different thresholds
- Single email analysis
- Whitelist/blacklist functionality
- Custom settings per user

## How It Works

### 1. Feature Extraction

The system extracts multiple features from emails:

**Content Features:**
- Keyword analysis (phishing-related terms)
- Text statistics (word count, sentence length, etc.)
- Urgency indicators (urgent, immediate, act now)
- Emotional manipulation patterns
- Vocabulary richness

**Pattern Features:**
- URL count and characteristics
- IP addresses in links
- Email addresses in content
- Special character usage

**Metadata Features:**
- Sender address analysis
- Header analysis (when available)
- Attachment presence

### 2. Threat Detection

The system uses two detection methods:

**ML-Based Detection (if model available):**
- Trained machine learning classifier
- Probability-based threat scoring
- Multiple threat categories

**Rule-Based Detection (fallback):**
- Heuristic rules for threat indicators
- Weighted scoring system
- High accuracy for common phishing patterns

### 3. Risk Assessment

Each email receives:
- **Threat Score:** 0.0 to 1.0 probability
- **Threat Type:** phishing, suspicious, legitimate
- **Confidence Level:** high, medium, low
- **Risk Factors:** Specific indicators found
- **Recommendations:** Actions to take

### 4. User-Specific Configuration

Each user profile includes:
- Custom threat threshold
- Auto-flag settings
- Whitelist (trusted senders)
- Blacklist (blocked senders)
- Statistics and history

## Advanced Usage

### Custom Threat Thresholds

Different users may want different sensitivity levels:

```python
# Security-conscious user (low threshold = more sensitive)
addon.setup_user_profile('paranoid_user', 'user1@example.com', 
                        threat_threshold=0.3)

# Regular user (medium sensitivity)
addon.setup_user_profile('normal_user', 'user2@example.com',
                        threat_threshold=0.6)

# Executive user (high threshold = less sensitive, fewer false positives)
addon.setup_user_profile('executive_user', 'user3@example.com',
                        threat_threshold=0.8)
```

### Batch Processing

```python
# Process multiple users at once
users = ['user1', 'user2', 'user3']

for username in users:
    scan_result = addon.scan_inbox(username)
    print(f"{username}: {scan_result['threats_found']} threats found")
```

### Testing with Sample Data

```python
# Generate test emails for a user
addon.add_sample_emails(
    username='test_user',
    count=20,              # Generate 20 emails
    phishing_ratio=0.3     # 30% will be phishing attempts
)

# Scan and evaluate
scan_results = addon.scan_inbox('test_user')
```

## API Reference

### GmailAddonIntegration

Main interface for the add-on system.

#### Methods

**`setup_user_profile(username, email, threat_threshold=0.6, auto_flag=True)`**
- Creates a new user profile
- Returns: `bool` - Success status

**`scan_inbox(username, auto_flag=None)`**
- Scans user's entire inbox for threats
- Returns: `dict` - Scan results with detected threats

**`analyze_single_email(username, email_data)`**
- Analyzes a single email
- Returns: `dict` - Analysis result with threat score

**`add_to_whitelist(username, sender_email)`**
- Adds sender to user's whitelist
- Returns: `bool` - Success status

**`add_to_blacklist(username, sender_email)`**
- Adds sender to user's blacklist
- Returns: `bool` - Success status

**`get_user_dashboard(username)`**
- Retrieves user statistics and dashboard
- Returns: `dict` - Dashboard data

**`update_addon_settings(username, **settings)`**
- Updates user's add-on configuration
- Returns: `bool` - Success status

**`list_all_profiles()`**
- Lists all configured user profiles
- Returns: `list` - Usernames

**`remove_user_profile(username)`**
- Removes user profile and disables add-on
- Returns: `bool` - Success status

## Email Data Format

When analyzing emails, provide data in this format:

```python
email_data = {
    'sender': 'sender@example.com',           # Required
    'sender_name': 'Sender Name',             # Optional
    'subject': 'Email Subject',               # Required
    'body': 'Email body content...',          # Required
    'urls': ['http://example.com/link'],      # Optional
    'attachments': ['file1.pdf', 'file2.doc'] # Optional
}
```

## Threat Score Interpretation

| Score Range | Interpretation | Action |
|-------------|---------------|---------|
| 0.0 - 0.3   | Legitimate | Safe to interact |
| 0.3 - 0.5   | Low Risk | Be cautious |
| 0.5 - 0.7   | Medium Risk | Verify sender |
| 0.7 - 0.9   | High Risk | Do not interact |
| 0.9 - 1.0   | Critical Risk | Report and delete |

## File Storage Structure

The system creates these directories:

```
user_profiles/         # User profile configurations
├── alice.json        # Alice's profile
├── bob.json          # Bob's profile
└── charlie.json      # Charlie's profile

simulated_inboxes/     # Simulated Gmail inboxes
├── alice_inbox.json   # Alice's inbox
├── bob_inbox.json     # Bob's inbox
└── charlie_inbox.json # Charlie's inbox
```

## Security Considerations

### For Development/Testing:
- This system uses a **simulated Gmail environment** for testing
- No actual Gmail API credentials required
- Safe for development and demonstration

### For Production:
To integrate with real Gmail:
1. Implement Gmail API authentication
2. Add OAuth 2.0 credentials
3. Replace `gmail_simulator.py` with actual Gmail API calls
4. Ensure proper data encryption
5. Comply with Gmail API terms of service

## Performance

- **Single Email Analysis:** < 100ms
- **Batch Scanning (100 emails):** < 5 seconds
- **Model Loading:** One-time ~500ms
- **Memory Usage:** ~50MB per user profile

## Troubleshooting

### Model Not Found
If you see "Model file not found", the system will automatically use rule-based detection, which works well for most phishing emails. To use ML detection, train a model first.

### NLTK Data Missing
Run `python setup_nltk.py` to download required data.

### Profile Already Exists
If you get "Profile already exists", you can either:
- Use a different username
- Update the existing profile with `update_addon_settings()`
- Delete the old profile with `remove_user_profile()`

## Examples

See `demo_gmail_addon.py` for complete examples of:
- Multi-user setup
- Inbox scanning
- Single email analysis
- Whitelist/blacklist management
- Custom settings per user

## Contributing

To extend the system:

1. **Add new features:** Extend `email_analyzer.py` or `feature_extractor.py`
2. **Improve detection:** Train better models with more data
3. **Add integrations:** Replace simulator with real email providers
4. **Enhance UI:** Build web interface or GUI

## License

This system is provided as-is for educational and demonstration purposes.

## Support

For questions or issues, refer to:
- `demo_gmail_addon.py` - Working examples
- `README.md` - Project overview
- Individual module docstrings - API documentation
