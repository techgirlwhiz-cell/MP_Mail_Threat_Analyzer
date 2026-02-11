# Gmail Add-on Quick Reference

## 🚀 Installation (One-Time Setup)

```bash
pip3 install -r requirements.txt
python3 setup_nltk.py
python3 test_addon.py
```

## 📝 Basic Usage

### Initialize System

```python
from gmail_addon_integration import GmailAddonIntegration
addon = GmailAddonIntegration()
```

### Setup User

```python
addon.setup_user_profile(
    username='john',
    email='john@example.com',
    threat_threshold=0.6,  # 0.0-1.0 (lower = more sensitive)
    auto_flag=True
)
```

### Analyze Single Email

```python
email = {
    'sender': 'sender@example.com',
    'subject': 'Email Subject',
    'body': 'Email content...',
    'urls': ['http://example.com']
}

result = addon.analyze_single_email('john', email)
# Returns: is_threat, threat_score, risk_factors, recommendations
```

### Scan Inbox

```python
results = addon.scan_inbox('john', auto_flag=True)
# Returns: total_scanned, threats_found, results[]
```

### Whitelist/Blacklist

```python
addon.add_to_whitelist('john', 'trusted@company.com')
addon.add_to_blacklist('john', 'spam@malicious.com')
```

### Get Dashboard

```python
dashboard = addon.get_user_dashboard('john')
# Returns: stats, settings, inbox_count, flagged_count
```

### Update Settings

```python
addon.update_addon_settings(
    'john',
    threat_threshold=0.5,
    auto_flag=True,
    notifications=True
)
```

## 📊 Sensitivity Levels

| Threshold | Level | Description |
|-----------|-------|-------------|
| 0.3 | Paranoid | Maximum protection |
| 0.5 | High | Strong protection |
| 0.6 | Medium | Balanced (default) |
| 0.7 | Low | Fewer false positives |
| 0.8 | Minimal | Only obvious threats |

## 🎯 Threat Scores

| Score | Risk Level | Action |
|-------|-----------|---------|
| 0.0-0.3 | Safe | Proceed normally |
| 0.3-0.5 | Low | Be cautious |
| 0.5-0.7 | Medium | Verify sender |
| 0.7-0.9 | High | Don't interact |
| 0.9-1.0 | Critical | Report & delete |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `gmail_addon_integration.py` | Main interface (use this) |
| `test_addon.py` | Test the system |
| `demo_gmail_addon.py` | See examples |
| `README_GMAIL_ADDON.md` | Full documentation |
| `INTEGRATION_GUIDE.md` | Integration examples |

## 🧪 Testing

```bash
# Check dependencies
python3 check_dependencies.py

# Run tests
python3 test_addon.py

# See demo
python3 demo_gmail_addon.py
```

## 🔧 Common Operations

### Add Multiple Users

```python
users = [
    ('alice', 'alice@company.com', 0.5),
    ('bob', 'bob@company.com', 0.6),
    ('charlie', 'charlie@company.com', 0.7)
]

for username, email, threshold in users:
    addon.setup_user_profile(username, email, threshold)
```

### Scan All Users

```python
for username in addon.list_all_profiles():
    results = addon.scan_inbox(username)
    print(f"{username}: {results['threats_found']} threats")
```

### Generate Test Emails

```python
addon.add_sample_emails(
    'john', 
    count=20,              # Number of emails
    phishing_ratio=0.3     # 30% phishing
)
```

## 📋 Email Data Format

```python
{
    'sender': 'email@example.com',     # Required
    'sender_name': 'Name',              # Optional
    'subject': 'Subject',               # Required
    'body': 'Content...',               # Required
    'urls': ['http://...'],             # Optional
    'attachments': ['file.pdf']         # Optional
}
```

## 🎛️ Analysis Result Format

```python
{
    'is_threat': True/False,
    'threat_score': 0.85,              # 0.0 to 1.0
    'threat_type': 'phishing',          # phishing/suspicious/legitimate
    'confidence': 'high',               # high/medium/low
    'risk_factors': [                   # List of issues found
        'Multiple phishing keywords',
        'Urgency manipulation detected'
    ],
    'recommendations': [                # What to do
        '⚠️ HIGH RISK - Do not interact',
        'Mark as spam immediately'
    ]
}
```

## 🚨 Troubleshooting

### "Module not found"
```bash
pip3 install -r requirements.txt
```

### "NLTK data missing"
```bash
python3 setup_nltk.py
```

### "Profile already exists"
```python
# Update instead of create
addon.update_addon_settings('john', threat_threshold=0.5)
# Or remove and recreate
addon.remove_user_profile('john')
```

## 📖 More Info

- **Full Guide**: `README_GMAIL_ADDON.md`
- **Setup**: `SETUP_INSTRUCTIONS.md`
- **Integration**: `INTEGRATION_GUIDE.md`
- **API Docs**: `GMAIL_ADDON_SETUP.md`
- **Examples**: `demo_gmail_addon.py`

## 🎯 Quick Examples

### Example 1: Basic Protection
```python
addon = GmailAddonIntegration()
addon.setup_user_profile('user', 'user@email.com')

email = {
    'sender': 'phishing@bad.com',
    'subject': 'URGENT!!!',
    'body': 'Verify your account now!',
    'urls': ['http://malicious.com']
}

result = addon.analyze_single_email('user', email)
if result['is_threat']:
    print(f"⚠️ Threat: {result['threat_score']:.0%}")
```

### Example 2: Multiple Users
```python
addon = GmailAddonIntegration()

# Setup team
for member in ['alice', 'bob', 'charlie']:
    addon.setup_user_profile(member, f'{member}@team.com')

# Scan all
for member in ['alice', 'bob', 'charlie']:
    scan = addon.scan_inbox(member)
    print(f"{member}: {scan['threats_found']} threats")
```

### Example 3: Custom Sensitivity
```python
# High sensitivity for security team
addon.setup_user_profile('sec', 'sec@co.com', 
                        threat_threshold=0.3)

# Low sensitivity for executives
addon.setup_user_profile('ceo', 'ceo@co.com',
                        threat_threshold=0.8)
```

## ✅ Quick Checklist

- [ ] Installed dependencies
- [ ] Ran test script
- [ ] Read README_GMAIL_ADDON.md
- [ ] Ran demo script
- [ ] Ready to integrate!

---

**Need help?** See full documentation in `README_GMAIL_ADDON.md`
