# 🔄 MailThreat Analyzer - System Flow

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     USER OPENS BROWSER                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │ Check if logged in?  │
           │ (token in localStorage)│
           └──────┬──────────┬────┘
                  │          │
         NO ◄─────┘          └─────► YES
         │                          │
         ▼                          ▼
┌────────────────┐          ┌──────────────┐
│  login.html    │          │  index.html  │
│  Login Page    │          │  Dashboard   │
└────────┬───────┘          └──────────────┘
         │
         ▼
┌─────────────────────────┐
│ User Enters Credentials │
│ - demo@example.com      │
│ - demo123               │
└─────────┬───────────────┘
          │
          ▼
┌──────────────────────────┐
│ POST /api/auth/login     │
│ Backend validates        │
│ - Check user exists      │
│ - Verify password hash   │
│ - Generate token         │
└──────────┬───────────────┘
           │
      SUCCESS?
           │
    ┌──────┴──────┐
    │             │
   YES           NO
    │             │
    ▼             ▼
┌────────────┐  ┌──────────────┐
│ Store in   │  │ Show error   │
│ localStorage│  │ message      │
│ - token    │  │ "Invalid..."  │
│ - email    │  └──────────────┘
│ - role     │
│ - name     │
└─────┬──────┘
      │
      ▼
┌──────────────────┐
│ Redirect to      │
│ Dashboard        │
└──────────────────┘
```

---

## Dashboard Usage Flow

```
┌──────────────────────────────────────────────────────────┐
│                    DASHBOARD LOADED                      │
└─────────┬────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────┐
│ Check Authentication         │
│ - Get token from localStorage│
│ - Validate token             │
└─────────┬────────────────────┘
          │
      VALID?
          │
    ┌─────┴─────┐
    │           │
   YES         NO
    │           │
    ▼           ▼
┌─────────┐  ┌──────────────────┐
│Continue │  │ Redirect to Login│
└────┬────┘  └──────────────────┘
     │
     ▼
┌──────────────────────────┐
│ Load User Profile        │
│ - Name                   │
│ - Email                  │
│ - Role                   │
└────┬─────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ Fetch Dashboard Data     │
│ GET /api/dashboard/stats │
│ (with auth token)        │
└────┬─────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ Display Statistics       │
│ - Total Scanned          │
│ - Threats Detected       │
│ - Threats Blocked        │
│ - Protection Score       │
└──────────────────────────┘
```

---

## Button Action Flow

### Add to Whitelist

```
User clicks "+ Add Sender" on Whitelist page
         │
         ▼
Modal dialog opens (addWhitelistModal)
         │
         ▼
User enters email: "trusted@example.com"
         │
         ▼
User clicks "Add to Whitelist"
         │
         ▼
Validate email format
         │
      VALID?
         │
    ┌────┴────┐
   YES       NO
    │         │
    ▼         ▼
POST to     Show error
/api/        toast
whitelist    │
    │         └──► "Invalid email"
    ▼
Backend adds email
    │
    ▼
Returns success
    │
    ▼
Close modal
    │
    ▼
Show success toast
"Added trusted@example.com to whitelist"
    │
    ▼
Refresh whitelist display
```

### Scan Now

```
User clicks "Scan Now" button
         │
         ▼
Show loading overlay
"Scanning emails..."
         │
         ▼
POST /api/scan/inbox
(with auth token)
         │
         ▼
Backend scans user's inbox
- Gets all emails
- Analyzes each with ML model
- Flags threats
         │
         ▼
Returns scan results
- Total scanned
- Threats found
- Threat rate
         │
         ▼
Hide loading overlay
         │
         ▼
Show success toast
"Scan completed! Found 3 new threats"
         │
         ▼
Refresh dashboard statistics
```

### Logout

```
User clicks "Logout" button
         │
         ▼
Show confirmation dialog
"Are you sure you want to logout?"
         │
         ▼
User confirms
         │
         ▼
Clear localStorage
- Remove authToken
- Remove userEmail
- Remove userRole
- Remove userName
         │
         ▼
POST /api/auth/logout
(invalidate token on backend)
         │
         ▼
Stop auto-refresh timer
         │
         ▼
Redirect to login.html
```

---

## API Request Flow

### Authenticated API Request

```
Frontend wants to fetch data
         │
         ▼
Prepare request with headers:
{
  "Authorization": "Bearer abc123token",
  "Content-Type": "application/json"
}
         │
         ▼
Send to backend endpoint
         │
         ▼
Backend @require_auth decorator
         │
         ▼
Extract token from Authorization header
         │
         ▼
Check if token exists in ACTIVE_TOKENS
         │
      VALID?
         │
    ┌────┴────┐
   YES       NO
    │         │
    ▼         ▼
Inject    Return 401
user info   Unauthorized
to request    │
    │         ▼
    ▼     Frontend
Process   redirects
request    to login
    │
    ▼
Return data
    │
    ▼
Frontend receives response
    │
    ▼
Update UI with data
```

---

## Data Flow Diagram

```
┌──────────────┐
│   Browser    │
│  (Frontend)  │
└───────┬──────┘
        │
        │ HTTP Requests
        │ (with token)
        ▼
┌──────────────────┐
│   Flask Backend  │
│  web_backend.py  │
└───────┬──────────┘
        │
        ├──► Authentication
        │    - Validate token
        │    - Check user exists
        │
        ├──► Gmail Add-on Integration
        │    └──► GmailAddonManager
        │         - User profiles
        │         - Settings
        │         - Statistics
        │
        ├──► Email Threat Detector
        │    └──► ML/NLP Analysis
        │         - Feature extraction
        │         - Threat scoring
        │         - Risk factors
        │
        └──► Gmail Simulator
             └──► Email Storage
                  - Inbox
                  - Flagged emails
                  - Whitelist
                  - Blacklist
```

---

## User Journey Map

### First Time User

```
1. Opens app → Sees login page
2. Enters credentials → Authenticated
3. Sees empty dashboard → Prompted to scan
4. Clicks "Scan Now" → System analyzes emails
5. Views flagged threats → Sees detailed analysis
6. Adds trusted senders → Whitelist updated
7. Adjusts settings → Preferences saved
8. Logs out → Session cleared
```

### Returning User

```
1. Opens app → Auto-logged in (if "Remember Me")
2. Dashboard shows latest stats → Up to date
3. Checks new flagged emails → Reviews threats
4. Takes actions → Deletes/Blocks/Whitelists
5. Scans periodically → Keeps inbox safe
6. Logs out when done → Session cleared
```

---

## Component Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Web Application                     │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  login.html  │  │  index.html  │  │ styles.css  │ │
│  │  login.js    │  │  app.js      │  │             │ │
│  └──────────────┘  └──────────────┘  └─────────────┘ │
│         │                 │                  │        │
│         └─────────────────┴──────────────────┘        │
│                          │                            │
└──────────────────────────┼────────────────────────────┘
                           │
                    HTTP/JSON API
                           │
┌──────────────────────────┼────────────────────────────┐
│                   Backend Server                      │
├──────────────────────────┼────────────────────────────┤
│                          │                            │
│  ┌────────────────────────────────────────────────┐  │
│  │          web_backend.py (Flask)                │  │
│  │  - Authentication endpoints                    │  │
│  │  - Dashboard endpoints                         │  │
│  │  - Email management endpoints                  │  │
│  │  - Settings endpoints                          │  │
│  └────────┬──────────────────────┬─────────────────┘  │
│           │                      │                    │
│  ┌────────▼──────────┐  ┌────────▼──────────────┐    │
│  │ gmail_addon_      │  │ email_threat_         │    │
│  │ integration.py    │  │ detector.py           │    │
│  │ - Profile mgmt    │  │ - ML/NLP analysis     │    │
│  │ - Settings        │  │ - Threat scoring      │    │
│  │ - Stats           │  │ - Risk assessment     │    │
│  └───────────────────┘  └───────────────────────┘    │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## Security Layers

```
┌───────────────────────────────────────────┐
│         Security Architecture             │
└───────────────────────────────────────────┘

Layer 1: Frontend Protection
├─ Check for valid token before rendering
├─ Redirect to login if no token
└─ Clear sensitive data on logout

Layer 2: Network Security
├─ HTTPS (in production)
├─ CORS configured
└─ Token in Authorization header

Layer 3: Backend Authentication
├─ @require_auth decorator on all endpoints
├─ Token validation on every request
└─ User context injection

Layer 4: Data Protection
├─ Password hashing (SHA-256)
├─ No passwords in logs
├─ Token expiration
└─ Secure token generation

Layer 5: Session Management
├─ Tokens stored in memory (ACTIVE_TOKENS)
├─ Auto-expiration after 1/30 days
├─ Logout invalidates token
└─ No sensitive data in localStorage
```

---

## System States

### Logged Out
- Can access: login.html only
- Cannot access: dashboard, any API endpoints
- State stored: Nothing in localStorage
- Token: None

### Logged In
- Can access: All pages, all API endpoints
- Cannot access: login.html (redirects to dashboard)
- State stored: token, email, role, name
- Token: Valid and active

### Session Expired
- Automatically logged out
- Redirected to login
- State cleared
- Must login again

---

## Quick Reference: URL Routes

### Frontend URLs
- `/login.html` - Login page
- `/index.html` or `/` - Dashboard (requires auth)

### Backend API URLs

#### Authentication
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/google/url`
- `GET /api/auth/verify`

#### Dashboard
- `GET /api/dashboard/stats`
- `GET /api/dashboard/recent-threats`

#### Emails
- `GET /api/flagged-emails`
- `GET /api/flagged-emails/<id>`
- `DELETE /api/flagged-emails/<id>`

#### Scanning
- `POST /api/scan/inbox`
- `POST /api/scan/email`

#### Reports
- `GET /api/reports/summary`
- `GET /api/reports/activity`

#### Lists
- `GET /api/whitelist`
- `POST /api/whitelist`
- `DELETE /api/whitelist/<email>`
- `GET /api/blacklist`
- `POST /api/blacklist`
- `DELETE /api/blacklist/<email>`

#### Settings
- `GET /api/settings`
- `PUT /api/settings`

---

This visual guide shows how all the pieces work together! 🎉
