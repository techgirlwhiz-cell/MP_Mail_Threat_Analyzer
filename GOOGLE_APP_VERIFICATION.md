# How to Remove "Google hasn't verified this app"

## Why you see it

Your OAuth app is in **Testing** mode. Google shows this warning for any app that hasn’t passed their verification process. It’s normal for development and internal use.

---

## Option 1: Keep testing (no change)

- **Best for:** Development, school projects, internal tools, limited users.
- **What to do:** Nothing. When users see the warning, they click **Advanced** → **Go to MailThreat Analyzer (unsafe)** and continue.
- **Limit:** Only **test users** you add in Google Cloud Console can sign in (up to 100). That’s enough for most coursework and internal use.

We’ve added a short tip on the login page so users know to click Advanced and continue.

---

## Option 2: Publish and verify (warning goes away)

To allow **any** Google user to sign in **without** the “unverified” warning, you must **publish** the app and complete **Google’s verification**.

### Steps (high level)

1. **Google Cloud Console**  
   - [APIs & Services → OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).

2. **Finish consent screen**  
   - App name, logo, support email, **Privacy Policy URL**, **Terms of Service URL**.  
   - Homepage URL (e.g. your app’s public URL).  
   - All scopes you use (e.g. Gmail read/modify, userinfo).

3. **Publish the app**  
   - On the OAuth consent screen, click **Publish app**.  
   - Choose **In production** (or follow the flow for external users).  
   - Until verification is done, only test users can sign in; the “unverified” screen may still show for others.

4. **Submit for verification**  
   - In the same consent screen area, use **Submit for verification** (or the equivalent for your app type).  
   - You’ll need:
     - Working **Privacy Policy** and **Terms of Service** pages (public URLs).
     - A short explanation of how the app uses the requested scopes (e.g. “Read Gmail to scan for threats”).
     - Sometimes a short video showing the sign-in and permission flow.
   - Google reviews the app (often 1–4+ weeks).  
   - Once approved, the “Google hasn’t verified this app” warning is removed for normal users.

### Notes

- Verification is required if you want **unlimited** users and **no** “unverified app” warning.
- For a university project or internal tool, **Option 1 (testing + tip on login)** is usually enough.

---

## Summary

| Goal                         | What to do |
|-----------------------------|------------|
| Keep it working as now      | Use the login page tip: **Advanced** → **Go to MailThreat Analyzer (unsafe)**. |
| Allow only your test users  | Add them under OAuth consent screen → Test users. No verification needed. |
| Allow anyone, no warning   | Publish app, add Privacy Policy + Terms, submit for Google verification. |

The tip on the login page is the quick “fix” for the message; verification is the way to remove it for everyone.
