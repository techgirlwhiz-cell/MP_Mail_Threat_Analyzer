# 📧 Gmail API Integration Setup Guide

## Complete Guide to Connect MailThreat Analyzer with Your Gmail

---

## 🎯 Overview

This guide will help you:
1. Enable Gmail API in Google Cloud Console
2. Set up OAuth 2.0 credentials
3. Connect your Gmail account for real-time scanning
4. Test the integration

---

## 📋 Prerequisites

- Google account (your Gmail)
- Access to Google Cloud Console
- Admin rights to your Gmail (for organizational setup)

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create New Project**
   - Click "Select a project" dropdown at the top
   - Click "NEW PROJECT"
   - Project name: "MailThreat Analyzer"
   - Click "CREATE"

3. **Wait for Project Creation**
   - Takes 10-20 seconds
   - You'll see a notification when ready

---

### Step 2: Enable Gmail API

1. **Open API Library**
   - In the left sidebar, click "APIs & Services" → "Library"
   - Or visit: https://console.cloud.google.com/apis/library

2. **Search for Gmail API**
   - Type "Gmail API" in the search box
   - Click on "Gmail API" from results

3. **Enable the API**
   - Click the blue "ENABLE" button
   - Wait for confirmation (takes a few seconds)

---

### Step 3: Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen**
   - Left sidebar: "APIs & Services" → "OAuth consent screen"
   - Or visit: https://console.cloud.google.com/apis/credentials/consent

2. **Choose User Type**
   - Select "External" (for testing with any Gmail)
   - Click "CREATE"

3. **Fill in App Information**
   
   **App Information:**
   - App name: `MailThreat Analyzer`
   - User support email: `[your email]`
   - App logo: (optional, skip for now)

   **App Domain:**
   - Application home page: `http://localhost:5001`
   - Privacy policy: (optional for testing)
   - Terms of service: (optional for testing)

   **Developer Contact:**
   - Email: `[your email]`

   Click "SAVE AND CONTINUE"

4. **Configure Scopes**
   - Click "ADD OR REMOVE SCOPES"
   - Search and select these scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.modify`
     - `https://www.googleapis.com/auth/userinfo.email`
     - `https://www.googleapis.com/auth/userinfo.profile`
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"

5. **Add Test Users**
   - Click "ADD USERS"
   - Enter your Gmail address
   - Click "ADD"
   - Click "SAVE AND CONTINUE"

6. **Review and Go Back**
   - Review your settings
   - Click "BACK TO DASHBOARD"

---

### Step 4: Create OAuth Credentials

1. **Go to Credentials**
   - Left sidebar: "APIs & Services" → "Credentials"
   - Or visit: https://console.cloud.google.com/apis/credentials

2. **Create OAuth Client ID**
   - Click "+ CREATE CREDENTIALS" at the top
   - Select "OAuth client ID"

3. **Configure OAuth Client**
   - Application type: Select "Web application"
   - Name: `MailThreat Analyzer Web Client`
   
   **Authorized JavaScript origins:**
   - Add: `http://localhost:5001`
   - Add: `http://127.0.0.1:5001`
   
   **Authorized redirect URIs:**
   - Add: `http://localhost:5001/auth/gmail/callback`
   - Add: `http://127.0.0.1:5001/auth/gmail/callback`
   
   Click "CREATE"

4. **Save Credentials**
   - A popup will show your credentials
   - **Client ID**: Copy this (starts with xxxxxxx.apps.googleusercontent.com)
   - **Client Secret**: Copy this
   - Click "DOWNLOAD JSON" to save the file
   - Click "OK"

---

### Step 5: Configure MailThreat Analyzer

1. **Create Configuration File**
   
   Create a file: `gmail_config.json` in your project folder:

   ```json
   {
     "client_id": "YOUR_CLIENT_ID_HERE.apps.googleusercontent.com",
     "client_secret": "YOUR_CLIENT_SECRET_HERE",
     "redirect_uri": "http://localhost:5001/auth/gmail/callback",
     "scopes": [
       "https://www.googleapis.com/auth/gmail.readonly",
       "https://www.googleapis.com/auth/gmail.modify",
       "https://www.googleapis.com/auth/userinfo.email",
       "https://www.googleapis.com/auth/userinfo.profile"
     ]
   }
   ```

2. **Or Set Environment Variables** (More secure):

   ```bash
   export GMAIL_CLIENT_ID="YOUR_CLIENT_ID_HERE"
   export GMAIL_CLIENT_SECRET="YOUR_CLIENT_SECRET_HERE"
   ```

---

### Step 6: Install Required Packages

```bash
source venv/bin/activate
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

### Step 7: Test the Integration

1. **Start the Server**
   ```bash
   ./start_dashboard.sh
   ```

2. **Open Dashboard**
   - Go to: http://localhost:5001

3. **Connect Gmail**
   - Click "Connect Gmail" button
   - Sign in with your Google account
   - Grant permissions to MailThreat Analyzer
   - You'll be redirected back to the dashboard

4. **Scan Emails**
   - Click "Scan Now" to scan your Gmail inbox
   - Watch as threats are detected and flagged!

---

## 🔐 Security Best Practices

### For Testing (Your Personal Gmail)

✅ **Do:**
- Use OAuth 2.0 (already configured)
- Store credentials securely
- Only grant necessary permissions
- Test with a separate test Gmail account

❌ **Don't:**
- Share your Client Secret
- Commit credentials to Git
- Use production Gmail without testing

### For Organization Deployment

1. **Use Google Workspace**
   - Set up Google Workspace admin console
   - Configure domain-wide delegation
   - Restrict app access to organization

2. **Service Account (Recommended for Organizations)**
   - Create a service account
   - Enable domain-wide delegation
   - Access all employee emails securely

3. **Encryption**
   - Store OAuth tokens encrypted
   - Use environment variables
   - Rotate credentials regularly

---

## 📊 What Gets Scanned

### MailThreat Analyzer will:

✅ **Read** (gmail.readonly):
- Email subject lines
- Email body content
- Sender information
- Received timestamps
- Email metadata

✅ **Modify** (gmail.modify):
- Add labels (e.g., "Threat Detected")
- Move emails to folders
- Mark as read/unread
- Flag emails

❌ **Cannot**:
- Delete emails permanently (needs delete scope)
- Send emails (needs send scope)
- Access other Google services

---

## 🏢 Organizational Setup

### For CEO/Managers to Deploy Org-Wide

1. **Google Workspace Admin Console**
   - Go to: https://admin.google.com
   - Sign in as admin

2. **Security → API Controls**
   - Go to "API controls"
   - Add "MailThreat Analyzer" to allowed apps
   - Configure domain-wide delegation

3. **Service Account Setup**
   - Create service account in Google Cloud
   - Download JSON key
   - Enable domain-wide delegation
   - Add to Workspace admin console

4. **Deploy for All Users**
   - Configure once, applies to all employees
   - Centralized monitoring by managers
   - No individual user setup needed

---

## 🧪 Testing Checklist

- [ ] Google Cloud project created
- [ ] Gmail API enabled
- [ ] OAuth consent screen configured
- [ ] Test users added
- [ ] OAuth credentials created
- [ ] Client ID and Secret saved
- [ ] Configuration file created
- [ ] Required packages installed
- [ ] Server running on port 5001
- [ ] Can connect Gmail successfully
- [ ] Test email scan works
- [ ] Threats detected correctly
- [ ] Labels applied in Gmail

---

## 🔄 How Real-Time Scanning Works

### Initial Scan
1. User connects Gmail account
2. System fetches last 100 emails
3. Each email is analyzed for threats
4. Threats are flagged automatically

### Continuous Monitoring
1. **Gmail Push Notifications** (recommended)
   - Gmail notifies system of new emails
   - Instant threat detection
   - No polling needed

2. **Periodic Polling** (fallback)
   - Check Gmail every 5 minutes
   - Scan new emails since last check
   - Update threat database

### What Happens to Threats
1. Email is scanned by ML/NLP model
2. If threat detected (score > threshold):
   - Email is flagged in Gmail
   - Label added: "⚠️ Potential Threat"
   - User notified in dashboard
   - Manager can see in org dashboard
3. User can review and take action

---

## 📈 Manager Dashboard Features

### What Managers/CEO Can See:

1. **Organization Overview**
   - Total employees monitored
   - Total threats detected today/week/month
   - Threat rate across organization
   - High-risk employees (most threats)

2. **Employee Details**
   - Each employee's threat statistics
   - Flagged emails count
   - Last scan time
   - Risk level

3. **Threat Analysis**
   - Top threat types (phishing, spam, malware)
   - Trend analysis
   - Time-based patterns
   - Sender analysis

4. **Privacy Note**
   - Managers see only statistics
   - Cannot read individual email content
   - Privacy-compliant monitoring

---

## 🆘 Troubleshooting

### "Access Blocked" Error

**Cause:** App not verified by Google

**Solution:**
1. In OAuth consent screen, click "PUBLISH APP"
2. Or add your email as test user
3. Click "Advanced" → "Go to MailThreat Analyzer" when prompted

### "Invalid Credentials" Error

**Check:**
- Client ID is correct
- Client Secret is correct
- Redirect URI matches exactly
- Configuration file has no typos

### "Insufficient Permission" Error

**Fix:**
- Check OAuth scopes are added correctly
- Re-authenticate and grant permissions
- Verify Gmail API is enabled

### Emails Not Scanning

**Debug:**
1. Check Gmail API quota (Google Cloud Console)
2. Verify OAuth token is valid
3. Check server logs for errors
4. Test with a simple email first

---

## 📞 Support

### Useful Links

- **Google Cloud Console**: https://console.cloud.google.com/
- **Gmail API Documentation**: https://developers.google.com/gmail/api
- **OAuth 2.0 Setup**: https://developers.google.com/identity/protocols/oauth2
- **API Quotas**: https://console.cloud.google.com/apis/api/gmail.googleapis.com/quotas

### Need Help?

1. Check error messages in terminal
2. Review Google Cloud Console logs
3. Verify all steps completed
4. Test with a fresh test account

---

## ✅ Quick Summary

1. ✅ Create Google Cloud project
2. ✅ Enable Gmail API
3. ✅ Configure OAuth consent screen
4. ✅ Add test users (your email)
5. ✅ Create OAuth credentials
6. ✅ Save Client ID and Secret
7. ✅ Configure MailThreat Analyzer
8. ✅ Install packages
9. ✅ Start server
10. ✅ Connect Gmail and test!

---

**Once configured, MailThreat Analyzer will continuously monitor all connected Gmail accounts and alert managers of potential threats!** 🎉
