# 🔐 Google Sign-In Setup Guide

## ✨ Overview

Your MailThreat Analyzer now supports **real Google Sign-In** using OAuth 2.0!

---

## 🚀 Quick Setup (5 Steps)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "**Create Project**" or select existing project
3. Name it: "MailThreat Analyzer" (or your choice)
4. Click "**Create**"

### Step 2: Enable Gmail API

1. In your project, go to "**APIs & Services**" → "**Library**"
2. Search for "**Gmail API**"
3. Click "**Enable**"
4. Wait for it to activate

### Step 3: Create OAuth Credentials

1. Go to "**APIs & Services**" → "**Credentials**"
2. Click "**Create Credentials**" → "**OAuth client ID**"
3. If prompted, configure OAuth consent screen:
   - **User Type**: External (for testing with your Gmail)
   - **App name**: MailThreat Analyzer
   - **User support email**: Your email
   - **Developer contact**: Your email
   - **Scopes**: Add these:
     - `gmail.readonly`
     - `gmail.modify`
     - `userinfo.email`
     - `userinfo.profile`
   - **Test users**: Add your Gmail address
   - Click "**Save and Continue**"

4. Back to Credentials:
   - **Application type**: Web application
   - **Name**: MailThreat Analyzer Web Client
   - **Authorized redirect URIs**: Add this:
     ```
     http://localhost:5001/api/auth/google/callback
     http://localhost:5001

     ```
   - Click "**Create**"

5. **Download the JSON** credentials file (or copy the Client ID and Secret)

### Step 4: Configure Your App

1. In your project folder, create `gmail_config.json`:
   ```bash
   cd "/Users/desrine/Documents/Major Project_V1"
   cp gmail_config.json.template gmail_config.json
   ```

2. Edit `gmail_config.json` with your credentials:
   ```json
   {
       "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
       "client_secret": "YOUR_CLIENT_SECRET",
       "project_id": "your-project-id",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "redirect_uris": [
           "http://localhost:5001/api/auth/google/callback"
       ]
   }
   ```

3. Replace:
   - `YOUR_CLIENT_ID` → Your actual Client ID from Google
   - `YOUR_CLIENT_SECRET` → Your actual Client Secret
   - `your-project-id` → Your project ID

### Step 5: Test It!

1. Start your server:
   ```bash
   ./start_app.sh
   ```

2. Go to login page:
   ```
   http://localhost:5001/login.html
   ```

3. Click "**Sign in with Google**"

4. Authorize with your Gmail

5. Done! You're logged in! 🎉

---

## 🎯 What Happens When You Sign In

### First-Time Login

1. **Click "Sign in with Google"** on login page
2. **Redirected to Google** - Choose your Gmail account
3. **Grant permissions**:
   - Read your email messages
   - Modify your email (for labeling threats)
   - View your email address
   - View your profile info
4. **Redirected back** to MailThreat Analyzer
5. **Name prompt appears** - Auto-generated from your email
   - Example: `john.doe@gmail.com` → "John Doe"
   - You can change it immediately
6. **Dashboard loads** with your Gmail connected!

### What Gets Accessed

✅ **What we CAN see:**
- Your email address
- Your name (from Google profile)
- Email messages (to scan for threats)
- Ability to label emails as threats

❌ **What we CANNOT do:**
- Send emails on your behalf
- Delete your emails
- Access other Google services
- Share your data with third parties

---

## 🔒 Security & Privacy

### Your Data
- **Stored locally** on your machine only
- **No cloud storage** of your emails
- **OAuth tokens** stored securely in server memory
- **Can revoke access** anytime from Google Account settings

### Permissions Explained

1. **`gmail.readonly`**
   - Read email messages
   - Scan for threats
   - View message metadata

2. **`gmail.modify`**
   - Add labels to emails (like "Threat")
   - Mark emails as flagged
   - Does NOT allow deletion or sending

3. **`userinfo.email`**
   - Your email address
   - For account identification

4. **`userinfo.profile`**
   - Your name from Google
   - Profile picture (not currently used)

---

## 🛠️ Troubleshooting

### "Google login not configured"

**Problem**: `gmail_config.json` doesn't exist

**Solution**:
```bash
cd "/Users/desrine/Documents/Major Project_V1"
cp gmail_config.json.template gmail_config.json
# Edit with your credentials
```

### "Invalid client" or "Error 400"

**Problem**: Wrong Client ID or Secret

**Solution**:
- Double-check your `gmail_config.json`
- Make sure you copied the full Client ID (ends with `.apps.googleusercontent.com`)
- Verify Client Secret has no extra spaces

### "Redirect URI mismatch"

**Problem**: Redirect URI not authorized in Google Console

**Solution**:
1. Go to Google Cloud Console
2. Credentials → Your OAuth Client
3. Add authorized redirect URI:
   ```
   http://localhost:5001/api/auth/google/callback
   ```

### "This app isn't verified"

**Expected**: Your app is in testing mode

**Solution**:
- Click "**Advanced**"
- Click "**Go to MailThreat Analyzer (unsafe)**"
- This is YOUR app, it's safe!
- For production, submit for Google verification

### "Access blocked: This app's request is invalid"

**Problem**: OAuth consent screen not configured

**Solution**:
1. Go to "APIs & Services" → "OAuth consent screen"
2. Add your Gmail to "Test users"
3. Make sure all required scopes are added

---

## 📝 Configuration File Format

### Complete `gmail_config.json` Example

```json
{
    "client_id": "123456789-abcdefghijk.apps.googleusercontent.com",
    "client_secret": "GOCSPX-abcdefghijklmnopqrstuvwxyz",
    "project_id": "mailthreat-analyzer-12345",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": [
        "http://localhost:5001/api/auth/google/callback"
    ]
}
```

### Where to Find Values

**Client ID**: 
- Google Cloud Console → Credentials
- Format: `123456789-abcdefg.apps.googleusercontent.com`

**Client Secret**:
- Google Cloud Console → Credentials
- Format: `GOCSPX-abc123def456`

**Project ID**:
- Google Cloud Console → Dashboard (top bar)
- Format: `your-project-name-12345`

---

## 🔄 How It Works (Technical)

### OAuth Flow

```
1. User clicks "Sign in with Google"
   ↓
2. Frontend requests auth URL from backend
   ↓
3. Backend generates Google OAuth URL with scopes
   ↓
4. User redirected to Google login
   ↓
5. User grants permissions
   ↓
6. Google redirects to /api/auth/google/callback
   ↓
7. Backend exchanges auth code for tokens
   ↓
8. Backend creates user session
   ↓
9. Frontend receives token and stores in localStorage
   ↓
10. User redirected to dashboard
```

### Backend Endpoints

- `GET /api/auth/google/url` - Get OAuth URL
- `GET /api/auth/google/callback` - Handle OAuth callback
- `POST /api/auth/update-name` - Update display name

---

## ✅ Testing Checklist

After setup, verify:

- [ ] `gmail_config.json` exists with your credentials
- [ ] Server starts without errors
- [ ] "Sign in with Google" button appears on login
- [ ] Clicking button redirects to Google
- [ ] Can select your Gmail account
- [ ] Permission screen shows correct app name
- [ ] After granting, redirected back to dashboard
- [ ] Name prompt appears (first login)
- [ ] Can change name in settings
- [ ] Gmail connection shows in settings
- [ ] Logout works correctly

---

## 🎉 Benefits of Google Sign-In

### For You
✨ **No password to remember** - Use your Google account
✨ **Faster login** - One click authentication
✨ **Automatic name** - Pulled from your Google profile
✨ **Real Gmail access** - Scan actual emails
✨ **Secure** - OAuth 2.0 industry standard

### For Your Organization
✨ **Centralized auth** - Leverage Google Workspace
✨ **Better security** - Google's authentication
✨ **Audit trail** - Track access in Google Admin
✨ **Easy onboarding** - No separate passwords
✨ **Revocable access** - Control from Google settings

---

## 🔐 Revoking Access

If you want to disconnect MailThreat Analyzer from your Gmail:

1. Go to [Google Account - Third-party apps](https://myaccount.google.com/permissions)
2. Find "MailThreat Analyzer"
3. Click "Remove Access"
4. Done! Access revoked immediately

---

## 📞 Support

### Need Help?

1. **Check `gmail_config.json`** - Most common issue
2. **Verify redirect URI** - Must match exactly
3. **Check test users** - Must be added in OAuth consent
4. **Review server logs** - Shows detailed errors

### Common Files

- `gmail_config.json` - Your OAuth credentials
- `gmail_client.py` - Gmail API client code
- `web_backend.py` - Authentication endpoints

---

## 🎯 Next Steps

After Google Sign-In works:

1. ✅ Test email scanning with real Gmail
2. ✅ Connect multiple accounts (if manager/CEO)
3. ✅ Set up threat detection for your inbox
4. ✅ Configure whitelist/blacklist
5. ✅ Customize your display name

---

**Your Google Sign-In is ready! Start protecting your Gmail!** 🎉🔐
