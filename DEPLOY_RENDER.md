# Deploy MailThreat Analyzer on Render

This guide walks you through deploying the web app (Flask + static UI) as a **Web Service** on [Render](https://render.com).

---

## 1. Prerequisites

- A [Render](https://render.com) account (free tier works).
- Your code in a **Git repository** (GitHub, GitLab, or Bitbucket). Push this project to a repo if you haven’t already.

---

## 2. Create a Web Service

1. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Web Service**.
2. Connect your repository and select the repo that contains this project.
3. Configure:
   - **Name:** e.g. `mailthreat-analyzer`
   - **Region:** Choose one (e.g. Oregon).
   - **Branch:** `main` (or your default branch).
   - **Runtime:** **Python 3**.
   - **Build Command:** (use the lighter file so the free-tier build succeeds)
     ```bash
     pip install -r requirements-render.txt
     ```
     To use full ML (sentence-transformers, SHAP) use `requirements.txt` and a **paid** instance.
   - **Start Command:** (must use Render's `PORT` or the app will never respond)
     ```bash
     bash render_start.sh
     ```
   - **Instance type:** Free (or paid if you use full `requirements.txt`).

---

## 3. Environment Variables

In the Web Service → **Environment** tab, add:

| Key | Value | Required |
|-----|--------|----------|
| `SECRET_KEY` | A random string (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`) | Yes |
| `RENDER_EXTERNAL_URL` | Your app URL, e.g. `https://mailthreat-analyzer.onrender.com` | Yes (for OAuth and Gmail) |

**For Google Sign-In / Gmail (optional):** If you set these, the app will create `gmail_config.json` at startup so you don't need to commit secrets:

| Key | Value |
|-----|--------|
| `GMAIL_CLIENT_ID` | Your Google OAuth client ID (e.g. `xxx.apps.googleusercontent.com`) |
| `GMAIL_CLIENT_SECRET` | Your Google OAuth client secret |
| `GMAIL_PROJECT_ID` | Optional; default `mailthreat-analyzer` |

Optional (if you use Supabase for auth):

| Key | Value |
|-----|--------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anon key |

**Important:** After the first deploy, copy the **live URL** from the Render dashboard and set `RENDER_EXTERNAL_URL` to that exact URL (e.g. `https://your-service-name.onrender.com`). No trailing slash.

---

## 4. Gmail OAuth (if you use “Connect Gmail”)

1. In [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials → your OAuth 2.0 Client ID.
2. Under **Authorized redirect URIs**, add:
   ```text
   https://YOUR-RENDER-URL.onrender.com/api/auth/google/callback
   ```
   (Replace with your actual Render URL.)
3. **Gmail config on Render:** Set environment variables `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` (and `RENDER_EXTERNAL_URL`). The app creates `gmail_config.json` at startup from these, so you don't need to commit the file.

---

## 5. Deploy

1. Click **Create Web Service**. Render will clone the repo, run the build command, and start the app with the start command.
2. Wait for the deploy to finish. The **Logs** tab shows build and runtime output.
3. Open the service URL (e.g. `https://mailthreat-analyzer.onrender.com`). Use `/login.html` to open the login page:
   ```text
   https://your-service-name.onrender.com/login.html
   ```

---

## 6. Demo logins (no Supabase)

If you’re not using Supabase, the in-memory demo users work as long as the same instance is running:

- **Email:** `demo@example.com` · **Password:** `demo123`
- **Email:** `employee@example.com` · **Password:** `employee123`

Note: On the free tier, the app may spin down after inactivity; in-memory data (including demo users and sessions) is lost when the instance restarts.

---

## 7. Optional: Blueprint (render.yaml)

The repo includes a `render.yaml` that describes the Web Service. To use it:

1. In Render Dashboard → **New** → **Blueprint**.
2. Connect the same repo and select it. Render will read `render.yaml` and create the web service.
3. After creation, set **Environment** variables (especially `SECRET_KEY` and `RENDER_EXTERNAL_URL`) as in step 3 above.

---

## 8. Check that the app is up

After deploy, open:

- **https://your-service.onrender.com/health**  
  You should see `{"status":"ok","service":"mailthreat-analyzer"}`. If this loads, the server is listening on `PORT` and Flask is running.
- **https://your-service.onrender.com/login.html**  
  Login page.

If `/health` never loads, check **Logs** in the Render dashboard:
- **Build logs:** Did `pip install -r requirements-render.txt` finish? If the build fails or times out, use `requirements-render.txt` (not `requirements.txt`) on the free tier.
- **Service logs:** Do you see `Listening on 0.0.0.0:XXXX`? If not, the start command may be wrong or the app may be crashing on import (check for Python tracebacks).

---

## 9. Troubleshooting

- **Build fails (e.g. timeout or out of memory)**  
  Some dependencies (e.g. `sentence-transformers`, `shap`) are heavy. If the build fails, you can try removing or making them optional in `requirements.txt` for the Render build, or use a paid instance with more memory.

- **502 Bad Gateway / Loading forever ("service waking up")**  
  The server must listen on the port Render provides. Use the start command:
  ```bash
  bash render_start.sh
  ```
  This script runs `gunicorn --bind 0.0.0.0:${PORT} web_backend:app` so the app responds to HTTP. If you don't use `$PORT`, Render can't reach your app and the page will load indefinitely.

- **Gmail OAuth “Redirect URI mismatch”**  
  Confirm the redirect URI in Google Cloud Console is exactly:
  `https://YOUR-RENDER-URL.onrender.com/api/auth/google/callback`  
  and that `RENDER_EXTERNAL_URL` in Render is set to `https://YOUR-RENDER-URL.onrender.com` (no trailing slash).

- **Static files (login/dashboard) not loading**  
  The app serves `web_ui/` as static files. Ensure the build does not delete or ignore the `web_ui` folder.

---

## Summary

| Step | Action |
|------|--------|
| 1 | Push code to GitHub/GitLab/Bitbucket |
| 2 | Create Web Service on Render, connect repo |
| 3 | Build: `pip install -r requirements.txt` |
| 4 | Start: `gunicorn --bind 0.0.0.0:$PORT web_backend:app` |
| 5 | Set `SECRET_KEY` and `RENDER_EXTERNAL_URL` (and Supabase if used) |
| 6 | Add Gmail redirect URI in Google Cloud if using Gmail |
| 7 | Deploy and open `https://your-app.onrender.com/login.html` |
