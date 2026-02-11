# MailThreat Analyzer – Application Overview

## How It Works End-to-End

### 1. **Login (Google)**  
- You sign in with Google at `http://localhost:5001/login.html`.  
- The app stores your **Gmail refresh token** so it can read your inbox for scanning.

### 2. **Scan (Real Gmail + ML/NLP)**  
- Click **“Scan Now”** on the dashboard.  
- If you’re connected with Gmail, the app:
  - Fetches up to **100 recent emails** from your Gmail via the Gmail API.
  - For each email it:
    - Extracts **subject**, **body**, **sender**, and **URLs** from the body.
    - Runs **NLP feature extraction** (e.g. phishing keywords, urgency, structure) via `EmailAnalyzer`.
    - Runs **threat detection** via `EmailThreatDetector` (ML model if `phishing_model.pkl` exists and matches; otherwise **rule-based** using the same NLP features).
  - Emails whose threat score is at or above your **threat threshold** are **flagged** and stored as “real Gmail flagged” for your account.

### 3. **Flagged Emails = Your Gmail**  
- The **Flagged Emails** page loads from the API (`/api/flagged-emails`), not mock data.  
- After a Gmail scan, the list shows **only emails from your real Gmail** that were flagged by the ML/NLP engine.  
- Clicking an email loads full details from the API (risk factors and recommendations from the analyzer).

### 4. **Dashboard Stats**  
- **Total scanned**, **threats detected**, and **last scan** come from the last scan (real Gmail or simulated).  
- **Recent threats** on the dashboard also use the same real Gmail flagged list when available.

---

## Components

| Component | Role |
|----------|------|
| **Gmail API** (`gmail_client.py`) | Fetches real emails when the user has connected Gmail (refresh token stored). |
| **EmailThreatDetector** (`email_threat_detector.py`) | Runs NLP features + ML (if model exists) or rule-based scoring. |
| **EmailAnalyzer** (`email_analyzer.py`) | NLP: phishing keywords, urgency, structure, URLs, etc. |
| **Web backend** (`web_backend.py`) | Stores refresh token, runs real Gmail scan, stores `REAL_GMAIL_FLAGGED`, serves `/api/flagged-emails` and `/api/scan/inbox`. |
| **Web UI** (`web_ui/app.js`) | Loads flagged emails from API, shows real risk factors/recommendations in the modal. |

---

## Optional: Train ML Model

- The app works **without** `phishing_model.pkl` using **rule-based + NLP** only.  
- To use a trained ML model (e.g. Random Forest) as well:
  1. Install dependencies and prepare a CSV with columns like `email_body`, `email_subject`, `from_address`, `urls`, `label` (1 = phishing, 0 = legitimate).
  2. Run:  
     `python3 train_model.py --data your_data.csv --output phishing_model.pkl --scale`  
- Note: the current `EmailThreatDetector` expects a specific feature set (from `EmailAnalyzer`). The script `train_model.py` uses `FeatureExtractor`, which has a different feature set; so the saved bundle may not plug in directly. The app is designed to work and flag your Gmail using **NLP + rule-based** detection even when no model file is present.

---

## Quick Test Checklist

1. **Login** with Google at `http://localhost:5001/login.html`.  
2. **Scan Now** – wait for “Scan completed! Found X threats.”  
3. Open **Flagged Emails** – list should show only emails from your Gmail that were flagged.  
4. Click an email – modal should show subject, sender, threat score, and risk factors/recommendations from the analyzer.

If the Flagged Emails list is empty after a scan, either no emails passed the threat threshold or the scan used the simulated inbox (e.g. no Gmail refresh token). Ensure you signed in with Google and that the backend has stored the refresh token (happens automatically on first Google login).
