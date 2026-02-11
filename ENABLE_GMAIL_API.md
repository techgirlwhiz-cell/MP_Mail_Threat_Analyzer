# Enable Gmail API (fix “not flagging email” / 403 error)

The error **"Gmail API has not been used in project ... or it is disabled"** means the Gmail API is not enabled for your Google Cloud project. Enable it once, then Scan will work.

---

## Steps (about 1 minute)

1. **Open this link** (for your project):
   - **https://console.cloud.google.com/apis/library/gmail.googleapis.com?project=70121931776**

2. **Click the blue "ENABLE" button** on that page.

3. **Wait 1–2 minutes** for it to take effect.

4. In the app, click **Scan Now** again. Your Gmail inbox should load and the email you sent yourself can be flagged.

---

## If the link doesn’t work

1. Go to **https://console.cloud.google.com/**
2. Select the project you use for this app (e.g. **mailthreat-analyzer** or the one with ID **70121931776**).
3. Open **APIs & Services** → **Library** (or **Enable APIs and Services**).
4. Search for **Gmail API**.
5. Open **Gmail API** and click **Enable**.

After enabling, run **Scan Now** again; no need to sign in again.
