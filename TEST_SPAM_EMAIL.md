# How to Test That the App Catches Spam/Phishing

Use one of these methods to create a test email that the detector should flag.

---

## Option 1: Send a test email to your own Gmail (recommended)

1. **Open Gmail** (in a browser or app) and **compose a new email**.
2. **Send it to yourself** (your same Gmail address).
3. **Use the subject and body below** (copy-paste). The detector looks for urgency words, “verify your account”, “click here”, and suspicious links.
4. **Send** the email.
5. In the app, click **“Scan Now”** on the dashboard.
6. Open **Flagged Emails** – this message should appear there with a high threat score.

### Subject (copy this)
```
URGENT: Verify Your Account - Action Required Immediately
```

### Body (copy this)
```
Dear User,

We have detected suspicious activity on your account. Your access has been temporarily suspended for security reasons.

You must verify your account immediately to avoid permanent lockout. Click here to confirm your identity and restore access:

http://secure-verify-account.example.com/login

This is a limited time offer. Act now or your account will expire within 24 hours.

Do not ignore this message. Update your password and confirm your login details now.

Best regards,
Security Team
```

Why it gets flagged: uses **urgent**, **verify**, **account**, **suspended**, **security**, **click here**, **verify**, **immediately**, **limited time**, **act now**, **update**, **password**, **login**, and a **suspicious URL** – all patterns the detector uses for phishing/spam.

---

## Option 2: Quick test with a shorter email

If you want something shorter to paste into Gmail:

**Subject:** `Your account has been suspended - verify now`

**Body:**
```
Your account will be locked. Click here to verify: http://fake-bank-secure.tk/verify
Update your password immediately. Act now.
```

---

## Option 3: Test without sending (simulated inbox)

If you’re **not** using “Sign in with Google” and only use the **simulated inbox**:

1. The app adds sample emails when you first sign up (including some phishing-like ones).
2. Or add your own: in the project folder, find the file for your user in `simulated_inboxes/` (e.g. `yourname@gmail.com_inbox.json` or similar). You can add a new object to the `emails` array with `subject`, `sender`, `body` like in the examples above, then run **Scan Now** and check **Flagged Emails**.

---

## What you should see when it works

- **Dashboard:** “Scan completed! Found 1 threats.” (or more).
- **Flagged Emails:** The test email listed with a **high threat %** (e.g. 70–95%) and type **Phishing** or **Suspicious**.
- **Clicking the email:** Modal shows risk factors (e.g. “Multiple phishing keywords detected”, “Urgency manipulation detected”) and recommendations.

If it doesn’t get flagged, try:
- Making the subject/body **more** urgent and adding more phrases like “verify your account”, “click here”, “act now”.
- Lowering your **threat threshold** in Settings (e.g. to 50% or 60%) so more emails are flagged.
