# Sign in when Google OAuth is blocked

## Your error

```
Connection failed
OAuth failed: ... Connection refused ... oauth2.googleapis.com
```

This means **your machine or network cannot reach Google’s servers** (e.g. firewall, VPN, or no internet). The app cannot complete “Sign in with Google” in that situation.

---

## Use email/password instead

You can always sign in **without Google**:

1. Open: **http://localhost:5001/login.html**
2. **Do not** click “Sign in with Google”.
3. Use a demo account:
   - **Email:** `demo@example.com`
   - **Password:** `demo123`

Or:

- **Email:** `employee@example.com`
- **Password:** `employee123`

After that you can use the dashboard, Scan Now, Flagged Emails, and Settings as usual. Only “Sign in with Google” and “Connect Gmail” need access to Google.

---

## If you want Google sign-in to work later

Something is blocking HTTPS to `oauth2.googleapis.com` (port 443). Check:

1. **Internet**
   - Can you open https://www.google.com in the browser?
   - If not, fix internet first.

2. **Firewall / security software**
   - Temporarily allow outbound HTTPS (port 443) for Python or your terminal/app.
   - Or try from another network (e.g. phone hotspot) to see if the problem is your current network.

3. **VPN**
   - If you use a VPN, try turning it off or switching region, then try “Sign in with Google” again.

4. **Corporate/school network**
   - Many block or restrict Google. Use email/password on that network, and try Google sign-in only on a network that allows it (e.g. home).

5. **Proxy**
   - If you must use a proxy, set it for Python, e.g.:
     - `export HTTP_PROXY=http://your-proxy:port`
     - `export HTTPS_PROXY=http://your-proxy:port`
   - Then restart the server and try again.

---

## Summary

- **Right now:** Sign in with **demo@example.com** / **demo123** (or **employee@example.com** / **employee123**) on the login page.
- **Later:** Fix network/firewall/VPN so your machine can reach `oauth2.googleapis.com`, then “Sign in with Google” can work.
