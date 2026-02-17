# MailThreat Analyzer — Full Development Overview

This document is the **complete method of development** and **technical overview** for the MailThreat Analyzer project. It covers architecture, tech stack, components, data flow, APIs, setup, and extension points.

---

## 1. Project Overview

### 1.1 Purpose

**MailThreat Analyzer** is an organizational email threat detection system that:

- Lets users sign in (email/password or Google OAuth) and connect Gmail.
- Scans inboxes (real Gmail or simulated) using **ML/NLP** to detect phishing, spam, and suspicious content.
- Flags threats and surfaces them on a **dashboard** and **Flagged Emails** tab.
- Supports **multi-user profiles**, per-user settings (threshold, whitelist/blacklist), and optional **Supabase** for persistence.

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BROWSER (User)                                  │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │         Web UI (Static)            │
                    │  login.html, index.html, app.js,   │
                    │  login.js, styles.css             │
                    └─────────────────┬─────────────────┘
                                      │ HTTP / REST (Bearer token)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Flask Backend (web_backend.py)                        │
│  Auth • Dashboard • Scan • Flagged Emails • Settings • Whitelist/Blacklist   │
└───┬─────────────────────┬─────────────────────┬─────────────────────────────┘
    │                     │                     │
    ▼                     ▼                     ▼
┌───────────────┐  ┌──────────────────┐  ┌─────────────────────────────────────┐
│ GmailAddon    │  │ Gmail Client      │  │ Persistence                          │
│ Integration   │  │ (Real Gmail API)  │  │ REAL_GMAIL_FLAGGED, disk, Supabase  │
│ (addon +      │  │ gmail_client.py   │  │ flagged_emails/*.json, user_profiles│
│  simulator)   │  │                   │  │ simulated_inboxes/*.json           │
└───────┬───────┘  └──────────────────┘  └─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ML/NLP Pipeline                                      │
│  EmailThreatDetector → EmailAnalyzer, FeatureExtractor, URLAnalyzer,         │
│  (optional) phishing_model.pkl, SHAP, risk breakdown                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

| Layer | Technology | Purpose |
|-------|------------|--------|
| **Frontend** | HTML5, CSS3, JavaScript (vanilla) | Login, dashboard, flagged emails, settings, modals |
| **Backend** | Python 3, Flask, Flask-CORS | REST API, auth, scan orchestration, static files |
| **Auth** | In-memory tokens + optional Supabase | Login, Google OAuth, session/API auth |
| **ML/NLP** | scikit-learn, NLTK, joblib, (optional) SHAP | Feature extraction, threat scoring, optional trained model |
| **Gmail** | Google OAuth 2.0, Gmail API (google-api-python-client) | Real inbox fetch, OAuth callback |
| **Simulation** | Custom (gmail_simulator.py) | Simulated inbox when Gmail not connected |
| **Persistence** | JSON files + optional Supabase/PostgreSQL | Flagged emails, user profiles, simulated inboxes |
| **URL/TLD** | tldextract, url_analyzer, (optional) python-whois | URL and domain analysis |

### 2.1 Key Dependencies (requirements.txt)

- **Web:** flask, flask-cors, gunicorn  
- **ML/NLP:** numpy, pandas, scikit-learn, nltk, beautifulsoup4, joblib  
- **URLs:** tldextract  
- **Google:** google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client  
- **Optional:** supabase, sentence-transformers, shap, python-whois  

---

## 3. Directory and File Structure

```
Major Project_V1/
├── web_backend.py              # Main Flask app: routes, auth, scan, flagged, settings
├── gmail_client.py              # Gmail OAuth + API: auth URL, callback, get_messages
├── gmail_addon_integration.py   # Orchestrator: addon manager + threat detector + simulator
├── gmail_addon_manager.py       # User profiles, stats, config (threshold, whitelist, etc.)
├── gmail_simulator.py           # Simulated inbox, folders, flag_email, get_flagged_emails
├── email_threat_detector.py     # ML/NLP threat scoring, risk breakdown, optional model
├── email_analyzer.py            # NLP: phishing keywords, urgency, structure
├── feature_extractor.py         # Combines email + URL + metadata + optional semantic/grammar
├── url_analyzer.py              # URL features, TLD, suspicious patterns
├── train_model.py               # Train phishing model from CSV
├── predict.py                   # CLI/script prediction (optional)
├── requirements.txt
├── start_app.sh                 # Start web server (sets TLDEXTRACT_CACHE, runs web_backend)
├── gmail_config.json            # Google OAuth client_id, client_secret, redirect_uris (gitignored)
├── gmail_config.json.template   # Template for gmail_config.json
├── web_ui/
│   ├── index.html               # Dashboard: stats, recent threats, nav, modals
│   ├── login.html               # Login form + Google button
│   ├── app.js                   # Dashboard logic: apiCall, auth, scan, flagged, settings
│   ├── login.js                 # Login form + Google OAuth redirect
│   └── styles.css               # Global + login + dashboard styles (glass UI, purple theme)
├── flagged_emails/              # Per-user JSON: flagged list (persisted)
├── user_profiles/               # Per-user JSON: addon config, stats (from addon manager)
├── simulated_inboxes/           # Per-user JSON: simulator inbox state
├── .tldextract_cache/           # Local tldextract cache (avoids ~/.cache permission issues)
├── database_schema.sql          # Supabase/PostgreSQL schema (organizations, users, scans, etc.)
├── setup_database.sql           # Alternative/supplementary DB setup
└── *.md                         # Docs: README, QUICK_START, GOOGLE_SIGNIN_SETUP, etc.
```

---

## 4. Core Components

### 4.1 Web Backend (web_backend.py)

- **Responsibilities:** Serve static files, REST API, authentication, session/state, orchestrate scan and flagged storage.
- **Auth:** `require_auth` decorator; token in `Authorization: Bearer <token>`; tokens and user data in memory (`ACTIVE_TOKENS`, `USERS_DB`). Optional Supabase for login.
- **Key globals:** `REAL_GMAIL_FLAGGED` (in-memory flagged per user), `USERS_DB` (email → password_hash, role, full_name, gmail_refresh_token, etc.).
- **Persistence:** `_load_flagged_from_disk` / `_save_flagged_to_disk` (JSON under `flagged_emails/`). User profiles and simulator state in `user_profiles/`, `simulated_inboxes/`.
- **Environment:** `TLDEXTRACT_CACHE` set to project-local `.tldextract_cache` to avoid filesystem permission issues.

### 4.2 Gmail Add-on Integration (gmail_addon_integration.py)

- **Role:** Single entry point for “add-on” behavior: user profiles, threat detection, and inbox source (simulator or real Gmail).
- **Uses:** `GmailAddonManager` (profiles, stats, whitelist/blacklist), `EmailThreatDetector` (score, risk factors), `GmailSimulator` (inbox, flag_email, get_flagged_emails).
- **Main methods:** `setup_user_profile`, `scan_inbox` (with auto_flag), `analyze_single_email`, `add_sample_emails`.

### 4.3 Gmail Client (gmail_client.py)

- **Role:** Google OAuth 2.0 and Gmail API.
- **Config:** Reads `gmail_config.json` (client_id, client_secret, redirect_uris, token_uri).
- **Methods:** `get_authorization_url`, `handle_oauth_callback` (exchange code for tokens, return user info + refresh_token), `authenticate_with_token`, `get_messages`, `get_message_details`.
- **Scopes:** gmail.readonly, gmail.modify, userinfo.email, userinfo.profile (and openid where used).

### 4.4 Gmail Simulator (gmail_simulator.py)

- **Role:** Simulated inbox when Gmail is not connected or API fails.
- **State:** Per-user inbox: emails list, folders (inbox, flagged, spam). Persisted under `simulated_inboxes/`.
- **Methods:** `create_inbox`, `get_inbox`, `flag_email`, `get_flagged_emails`, `add_email`, `generate_sample_emails`.

### 4.5 Email Threat Detector (email_threat_detector.py)

- **Role:** Score each email (0–1), threat type, risk factors, recommendations; optional SHAP and risk breakdown.
- **Uses:** `EmailAnalyzer`, `FeatureExtractor`, `URLAnalyzer`; optional `phishing_model.pkl` (joblib bundle).
- **Behavior:** If model present and compatible, use it; else rule-based scoring using same feature set. Returns `threat_score`, `threat_type`, `risk_factors`, `recommendations`, etc.

### 4.6 Frontend (web_ui)

- **login.html / login.js:** Email/password submit to `POST /api/auth/login`; “Sign in with Google” gets URL from `GET /api/auth/google/url` and redirects. Token and user info stored in `localStorage`; redirect to `index.html`.
- **index.html:** Dashboard layout: stats, recent threats, nav (Dashboard, Flagged Emails, Scan History, Settings, Whitelist/Blacklist). Buttons: Scan Now, Connect Gmail, Logout, etc.
- **app.js:** On load: `checkAuthentication()` (redirect to login if no token); then `loadDashboardData()` (stats + recent threats), `loadFlaggedEmails()` when on Flagged tab. All API calls use `apiCall(endpoint, method, data)` with `Authorization: Bearer`. Handlers: `handleScanNow`, `handleSaveSettings`, whitelist/blacklist, modals (view email, add whitelist/blacklist). Flagged list sorted by backend (newest first).
- **styles.css:** Theming (e.g. purple/off-white), glass-style panels, responsive layout.

---

## 5. Data Flow

### 5.1 Authentication

1. **Email/password:** POST `/api/auth/login` → validate against `USERS_DB` (hash) → create token → return token + user (email, role, full_name). Frontend stores in `localStorage`, redirects to dashboard.
2. **Google:** Frontend calls `/api/auth/google/url` → backend returns Google auth URL + state (stored in session). User signs in at Google; Google redirects to `/api/auth/google/callback?code=...&state=...`. Backend exchanges code for tokens, gets user info, creates/updates user in `USERS_DB`, stores `gmail_refresh_token`, returns HTML that sets `localStorage` and redirects to dashboard.

### 5.2 Scan Flow

1. User clicks **Scan Now** → frontend `POST /api/scan/inbox` with Bearer token.
2. Backend resolves `current_user` from token. If user has `gmail_refresh_token`: use `GmailClient` to fetch messages (Gmail API); for each message run `EmailThreatDetector.analyze_email`; if score ≥ threshold, append to `REAL_GMAIL_FLAGGED[current_user]` and `_save_flagged_to_disk`. If Gmail fails (auth or API error), fallback to simulator.
3. If no refresh token (or fallback): use `GmailAddonIntegration.scan_inbox(current_user, auto_flag=True)` (simulator). Simulator flags threats; then `_persist_simulator_flagged(current_user)` writes simulator-flagged list into `REAL_GMAIL_FLAGGED` and disk so dashboard and Flagged tab stay in sync.
4. Response: `{ success, data: { totalScanned, threatsFound, threatRate, source: 'gmail'|'simulated' } }`.

### 5.3 Flagged Emails and Dashboard

- **Flagged tab:** GET `/api/flagged-emails`. Backend prefers live simulator list when present (so new flags show immediately), else uses `REAL_GMAIL_FLAGGED` / disk. List sorted newest first (`_sort_flagged_newest_first`).
- **Dashboard recent threats:** GET `/api/dashboard/recent-threats`. Same preference: simulator list if any, else persisted flagged; returns last 5, newest first.
- **Dashboard stats:** GET `/api/dashboard/stats` from addon manager (and optional Supabase) for total scanned, threats detected, last scan.

### 5.4 Settings, Whitelist, Blacklist

- Stored in addon manager (user profile JSON) and optionally synced to Supabase. API: GET/PUT `/api/settings`, GET/POST/DELETE `/api/whitelist`, GET/POST/DELETE `/api/blacklist`. Scan logic skips whitelisted senders and treats blacklisted as threats.

---

## 6. API Reference (Summary)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/login` | No | Email/password login; returns token + user |
| GET | `/api/auth/google/url` | No | Returns Google OAuth URL + state |
| GET | `/api/auth/google/callback` | No | OAuth callback; sets token via HTML redirect |
| POST | `/api/auth/logout` | Yes | Invalidates token |
| GET | `/api/auth/verify` | Yes | Returns current user info |
| POST | `/api/auth/update-name` | Yes | Update display name |
| GET | `/api/dashboard/stats` | Yes | Stats: total scanned, threats, last scan |
| GET | `/api/dashboard/recent-threats` | Yes | Last 5 threats (newest first) |
| GET | `/api/flagged-emails` | Yes | All flagged emails (newest first) |
| GET | `/api/flagged-emails/<id>` | Yes | Single flagged email details |
| DELETE | `/api/flagged-emails/<id>` | Yes | Remove from flagged list |
| POST | `/api/scan/inbox` | Yes | Run inbox scan (Gmail or simulator) |
| POST | `/api/scan/email` | Yes | Scan single email payload |
| GET/PUT | `/api/settings` | Yes | Threat threshold, auto-flag, notifications |
| GET/POST/DELETE | `/api/whitelist` | Yes | Whitelist management |
| GET/POST/DELETE | `/api/blacklist` | Yes | Blacklist management |
| GET | `/api/reports/summary` | Yes | Report summary |
| GET | `/api/reports/activity` | Yes | Activity timeline |

All “Yes” auth routes require header: `Authorization: Bearer <token>`.

---

## 7. Development Setup

### 7.1 Prerequisites

- Python 3 (3.10+ recommended)
- Google Cloud project with Gmail API and OAuth consent screen (for Google sign-in and real Gmail scan)

### 7.2 Local Run

```bash
# From project root
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Google OAuth: copy and edit config
cp gmail_config.json.template gmail_config.json
# Set client_id, client_secret, redirect_uris (e.g. http://localhost:5001/api/auth/google/callback)

# Start server (preferred: sets TLDEXTRACT_CACHE)
./start_app.sh
# Or: export TLDEXTRACT_CACHE="$(pwd)/.tldextract_cache"; python3 web_backend.py
```

- App: **http://localhost:5001**  
- Login: **http://localhost:5001/login.html**  
- Demo: `demo@example.com` / `demo123`, or Google (if configured).

### 7.3 Environment / Config

- **Port:** Default 5001 (`PORT` env or `web_backend.py`).
- **TLDEXTRACT_CACHE:** Set to project `.tldextract_cache` (in `web_backend.py` and `start_app.sh`) to avoid “Operation not permitted” on some systems.
- **OAuth:** `OAUTHLIB_INSECURE_TRANSPORT=1` and `OAUTHLIB_RELAX_TOKEN_SCOPE=1` for local HTTP and scope flexibility.
- **Supabase:** Optional; configure in `user_auth.py` and use `setup_database.sql` / `database_schema.sql` for schema.

---

## 8. Configuration and Deployment

- **gmail_config.json:** Required for Google sign-in and real Gmail scan. Not committed; use `gmail_config.json.template` as reference.
- **Supabase:** For production user/org persistence, run `database_schema.sql` (and any `setup_*.sql`) in the Supabase SQL editor; point backend to Supabase URL and key.
- **Production:** Use gunicorn (or another WSGI server) and HTTPS; set proper redirect URIs in Google Cloud and in `gmail_config.json`. See `render.yaml` / `DEPLOY_RENDER.md` if using Render.

---

## 9. Testing and Scripts

- **test_addon.py:** Exercises addon manager, simulator, threat detector, scan.
- **demo_gmail_addon.py:** Demo flow for multiple users and scans.
- **check_dependencies.py:** Validates installed packages.
- **train_model.py:** Train a phishing classifier from CSV; output can be used by `EmailThreatDetector` when the bundle format matches.

---

## 10. Extension Points and Modularity

- **Add-on per user:** `GmailAddonIntegration.setup_user_profile` adds a user to the addon manager and simulator; scan and settings are per-user.
- **Threat engine:** Swap or extend `EmailThreatDetector` and feature pipelines (`EmailAnalyzer`, `URLAnalyzer`, `FeatureExtractor`, optional semantic/grammar/behavioral extractors).
- **Inbox source:** Real Gmail vs simulator is chosen in `scan_inbox` based on presence of `gmail_refresh_token` and API success.
- **Persistence:** Flagged emails can be extended to Supabase (e.g. `email_scans` table) while keeping the same API contract. User profiles already support file-based and optional DB-backed storage.
- **UI:** New dashboard sections or tabs can call new endpoints; reuse `apiCall()` and existing auth.

---

## 11. Document Map

| Document | Use |
|----------|-----|
| **DEVELOPMENT_OVERVIEW.md** (this file) | Full development method and technical overview |
| **README.md** | Project intro, ML training, quick start |
| **QUICK_START.md** | Short run instructions |
| **APPLICATION_OVERVIEW.md** | End-to-end behavior and components |
| **SYSTEM_FLOW.md** | Auth and dashboard flow diagrams |
| **GOOGLE_SIGNIN_SETUP.md** | Google OAuth and Gmail API setup |
| **GOOGLE_APP_VERIFICATION.md** | Removing “app not verified” (publish/verify) |
| **AUTHENTICATION_GUIDE.md** | Auth flows and tokens |
| **WEB_UI_README.md** / **WEB_UI_START.md** | Web UI structure and startup |
| **database_schema.sql** | Supabase/PostgreSQL schema |

---

This development overview reflects the current codebase and is the single reference for the **entire method of development** and **complete technical overview** of the MailThreat Analyzer project.
