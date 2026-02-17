"""
Web Backend API for Email Threat Protection Dashboard
Flask API that connects the web UI to the Gmail add-on system
"""

import os
# Allow HTTP for OAuth on localhost (development only; use HTTPS in production)
os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')
# Allow scope order/difference from Google (e.g. openid added, different order)
os.environ.setdefault('OAUTHLIB_RELAX_TOKEN_SCOPE', '1')
# Use project-local cache for tldextract to avoid "Operation not permitted" on ~/.cache (macOS)
_project_dir = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('TLDEXTRACT_CACHE', os.path.join(_project_dir, '.tldextract_cache'))

import json as _json
# On Render (or any host): create gmail_config.json from env if missing (so no secrets in repo)
_gmail_config_path = os.path.join(_project_dir, 'gmail_config.json')
if not os.path.exists(_gmail_config_path):
    _cid = os.environ.get('GMAIL_CLIENT_ID', '').strip()
    _csec = os.environ.get('GMAIL_CLIENT_SECRET', '').strip()
    if _cid and _csec:
        _base = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5001').strip().rstrip('/')
        _redirect = f"{_base}/api/auth/google/callback"
        with open(_gmail_config_path, 'w') as f:
            _json.dump({
                'client_id': _cid,
                'client_secret': _csec,
                'project_id': os.environ.get('GMAIL_PROJECT_ID', 'mailthreat-analyzer'),
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'redirect_uris': [_redirect]
            }, f, indent=4)
        print("[Config] Created gmail_config.json from env")

from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
import json
import re
import secrets
import hashlib

# Import the Gmail add-on integration
from gmail_addon_integration import GmailAddonIntegration

# Optional: Supabase auth for email/password (falls back to USERS_DB if unavailable)
try:
    from user_auth import sign_in as supabase_sign_in
    SUPABASE_AUTH_AVAILABLE = True
except Exception:
    supabase_sign_in = None
    SUPABASE_AUTH_AVAILABLE = False

app = Flask(__name__, static_folder='web_ui', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app, supports_credentials=True)  # Enable CORS for all routes

# Initialize the Gmail add-on
addon = GmailAddonIntegration()

# In-memory user store (replace with database in production)
# Format: { email: { password_hash, role, full_name, created_at, ... } }
USERS_DB = {
    'demo@example.com': {
        'password_hash': hashlib.sha256('demo123'.encode()).hexdigest(),
        'role': 'ceo',
        'full_name': 'Demo User',
        'organization': 'dezrine\'s Org',
        'created_at': '2026-01-24',
        'gmail_connected': False
    },
    'employee@example.com': {
        'password_hash': hashlib.sha256('employee123'.encode()).hexdigest(),
        'role': 'employee',
        'full_name': 'Test Employee',
        'organization': 'dezrine\'s Org',
        'created_at': '2026-01-24',
        'gmail_connected': False
    }
}

# In-memory token store (replace with Redis/database in production)
ACTIVE_TOKENS = {}

# Member since date per email (set on login from Supabase or USERS_DB)
EMAIL_MEMBER_SINCE = {}

# One-time codes for "Connect Gmail" (link to current user) so callback works without session
# Format: { "shortcode": email }
OAUTH_LINK_CODES = {}


def get_public_base_url():
    """Base URL for OAuth redirects. Use RENDER_EXTERNAL_URL on Render, or request host + scheme."""
    external = os.environ.get('RENDER_EXTERNAL_URL', '').strip().rstrip('/')
    if external:
        return external
    if request:
        scheme = 'https' if request.headers.get('X-Forwarded-Proto') == 'https' else request.scheme
        return f'{scheme}://{request.host}'
    return 'http://localhost:5001'  # fallback when not in request context

# Real Gmail scan results: { user_email: [ { id, subject, sender, ..., received_at, flagged_at }, ... ] }
REAL_GMAIL_FLAGGED = {}

# Persistent store for flagged emails (survives server restart)
FLAGGED_EMAILS_DIR = Path('flagged_emails')


def _sanitize_email_for_path(email):
    return email.replace('@', '_at_').replace('.', '_')


def _path_for_flagged(user):
    FLAGGED_EMAILS_DIR.mkdir(exist_ok=True)
    return FLAGGED_EMAILS_DIR / f"{_sanitize_email_for_path(user)}.json"


def _load_flagged_from_disk(user):
    path = _path_for_flagged(user)
    if not path.exists():
        return []
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return []


def _save_flagged_to_disk(user, flagged_list):
    path = _path_for_flagged(user)
    try:
        with open(path, 'w') as f:
            json.dump(flagged_list, f, indent=2)
    except Exception as e:
        print(f"[Flagged] Could not save: {e}")


# ============================================
# Authentication Middleware
# ============================================

def require_auth(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        token = auth_header.split(' ')[1]
        
        if token not in ACTIVE_TOKENS:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Add user info to request context
        request.user_email = ACTIVE_TOKENS[token]['email']
        request.user_role = ACTIVE_TOKENS[token]['role']
        
        return f(*args, **kwargs)
    
    return decorated_function


def hash_password(password):
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token():
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def format_member_since(iso_date_or_str):
    """Format created_at or 'YYYY-MM-DD' to 'Mon DD, YYYY' for display."""
    if not iso_date_or_str:
        return None
    try:
        s = str(iso_date_or_str)
        if 'T' in s:
            dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(s[:10], '%Y-%m-%d')
        return dt.strftime('%b %d, %Y')
    except Exception:
        return None


# ============================================
# Authentication API Endpoints
# ============================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint. Tries Supabase Auth first; falls back to in-memory USERS_DB."""
    try:
        data = request.json
        email = (data.get('email') or '').strip().lower()
        password = data.get('password')
        remember_me = data.get('rememberMe', False)
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        user = None
        full_name = email.split('@')[0].title()
        role = 'employee'
        organization = 'Unknown'
        gmail_connected = False
        member_since_str = None
        
        # 1) Try Supabase Auth (saves users in Supabase; use Supabase Dashboard to manage)
        if SUPABASE_AUTH_AVAILABLE and supabase_sign_in:
            try:
                resp = supabase_sign_in(email, password)
                if resp and getattr(resp, 'user', None):
                    u = resp.user
                    if hasattr(u, 'get'):
                        meta = (u.get('user_metadata') or {})
                        full_name = meta.get('full_name') or (u.get('email') or email).split('@')[0].title()
                        created = u.get('created_at')
                    else:
                        meta = getattr(u, 'user_metadata', None) or {}
                        full_name = meta.get('full_name', email.split('@')[0].title()) if isinstance(meta, dict) else email.split('@')[0].title()
                        created = getattr(u, 'created_at', None)
                    member_since_str = format_member_since(created)
                    if member_since_str:
                        EMAIL_MEMBER_SINCE[email] = member_since_str
                    user = {'full_name': full_name, 'role': role, 'organization': organization, 'gmail_connected': gmail_connected}
            except Exception:
                # Supabase auth failed (wrong password, user not found, etc.) -> try fallback
                pass
        
        # 2) Fallback: in-memory USERS_DB (demo@example.com / employee@example.com)
        if not user:
            user = USERS_DB.get(email)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Invalid email or password'
                }), 401
            password_hash = hash_password(password)
            if password_hash != user['password_hash']:
                return jsonify({
                    'success': False,
                    'error': 'Invalid email or password'
                }), 401
            full_name = user.get('full_name', full_name)
            role = user['role']
            organization = user.get('organization', organization)
            gmail_connected = user.get('gmail_connected', False)
            member_since_str = format_member_since(user.get('created_at'))
            if member_since_str:
                EMAIL_MEMBER_SINCE[email] = member_since_str
        
        # Generate token and session
        token = generate_token()
        expiration = datetime.now() + timedelta(days=30 if remember_me else 1)
        ACTIVE_TOKENS[token] = {
            'email': email,
            'role': role,
            'full_name': full_name,
            'expires_at': expiration
        }
        
        # Setup user profile if doesn't exist
        profile = addon.addon_manager.get_profile(email)
        if not profile:
            addon.setup_user_profile(email, email, 0.6, True)
            addon.add_sample_emails(email, count=15, phishing_ratio=0.3)
        
        is_first_login = (full_name or '') == '' or full_name == email.split('@')[0].title()
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'email': email,
                'role': role,
                'full_name': full_name,
                'organization': organization,
                'is_first_login': is_first_login,
                'gmail_connected': gmail_connected,
                'member_since': member_since_str or EMAIL_MEMBER_SINCE.get(email)
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout endpoint."""
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        
        # Remove token
        if token in ACTIVE_TOKENS:
            del ACTIVE_TOKENS[token]
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auth/google/url', methods=['GET'])
def get_google_auth_url():
    """Get Google OAuth URL. If request has valid Bearer token, treat as 'Connect Gmail' (link to current user)."""
    try:
        if not os.path.exists('gmail_config.json'):
            return jsonify({
                'success': False,
                'error': 'Gmail not configured. Please create gmail_config.json with your OAuth credentials.'
            }), 400
        
        from gmail_client import GmailClient
        
        redirect_uri = get_public_base_url() + '/api/auth/google/callback'
        link_user = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
            if token in ACTIVE_TOKENS:
                link_user = ACTIVE_TOKENS[token]['email']
        
        gmail = GmailClient('gmail_config.json')
        if link_user:
            # "Connect Gmail" from dashboard: state survives redirect without session
            code = secrets.token_urlsafe(16)
            OAUTH_LINK_CODES[code] = link_user
            state = 'link:' + code
            auth_url, state = gmail.get_authorization_url(redirect_uri=redirect_uri, state=state)
        else:
            auth_url, state = gmail.get_authorization_url(redirect_uri=redirect_uri)
            session['oauth_state'] = state
        
        return jsonify({
            'success': True,
            'url': auth_url,
            'state': state
        })
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Gmail configuration file not found. Please set up OAuth credentials first.'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _oauth_escape_js(s):
    """Escape string for safe use inside a JavaScript single-quoted string."""
    if s is None:
        return ''
    s = str(s).replace('\\', '\\\\').replace("'", "\\'").replace('\r', '').replace('\n', '\\n')
    return s


@app.route('/api/auth/google/callback', methods=['GET'])
def google_callback():
    """Handle Google OAuth callback. Supports 'link Gmail' (from dashboard) and 'sign in with Google'."""
    try:
        from gmail_client import GmailClient
        
        authorization_response = request.url
        state = request.args.get('state') or session.get('oauth_state')
        
        if not state:
            return _oauth_error_page('Invalid OAuth state. Please try connecting Gmail again from the dashboard.')
        
        redirect_uri = get_public_base_url() + '/api/auth/google/callback'
        gmail = GmailClient('gmail_config.json')
        user_info = gmail.handle_oauth_callback(authorization_response, state, redirect_uri=redirect_uri)
        
        email = user_info['email']
        full_name = user_info.get('name', email.split('@')[0]) or email.split('@')[0]
        refresh_token = user_info.get('refresh_token') or ''
        
        # "Connect Gmail" from dashboard: link this Gmail to the current app user
        if isinstance(state, str) and state.startswith('link:'):
            code = state[5:].strip()
            link_email = OAUTH_LINK_CODES.pop(code, None)
            if link_email:
                if link_email not in USERS_DB:
                    USERS_DB[link_email] = {
                        'password_hash': '',
                        'role': 'employee',
                        'full_name': link_email.split('@')[0],
                        'organization': "dezrine's Org",
                        'created_at': datetime.now().isoformat(),
                        'gmail_connected': False,
                    }
                USERS_DB[link_email]['gmail_connected'] = True
                USERS_DB[link_email]['gmail_refresh_token'] = refresh_token
                profile = addon.addon_manager.get_profile(link_email)
                if not profile:
                    addon.setup_user_profile(link_email, link_email, 0.6, True)
                return _oauth_success_page(link_flow=True)
        
        # Sign in with Google (login page flow)
        if email not in USERS_DB:
            USERS_DB[email] = {
                'password_hash': '',
                'role': 'employee',
                'full_name': full_name,
                'organization': "dezrine's Org",
                'created_at': datetime.now().isoformat(),
                'auth_method': 'google',
                'gmail_connected': True,
                'gmail_refresh_token': refresh_token
            }
        else:
            USERS_DB[email]['gmail_connected'] = True
            USERS_DB[email]['full_name'] = full_name
            USERS_DB[email]['gmail_refresh_token'] = refresh_token
        
        token = generate_token()
        expiration = datetime.now() + timedelta(days=30)
        ACTIVE_TOKENS[token] = {
            'email': email,
            'role': USERS_DB[email]['role'],
            'full_name': full_name,
            'expires_at': expiration
        }
        profile = addon.addon_manager.get_profile(email)
        if not profile:
            addon.setup_user_profile(email, email, 0.6, True)
            addon.add_sample_emails(email, count=15, phishing_ratio=0.3)
        
        role_esc = _oauth_escape_js(USERS_DB[email]['role'])
        return _oauth_success_page(link_flow=False, token=token, email=email, full_name=full_name, role=role_esc)
    
    except Exception as e:
        err_str = str(e).lower()
        # Network/connectivity to Google blocked or unavailable
        if 'connection refused' in err_str or 'max retries exceeded' in err_str or 'oauth2.googleapis.com' in err_str:
            return _oauth_error_page(
                'Cannot reach Google (connection refused). Sign in with email/password below, or check: '
                'internet connection, firewall/VPN blocking HTTPS to Google, or try another network.',
                status_code=503,
                show_login_link=True
            )
        return _oauth_error_page(f'OAuth failed: {str(e)}', status_code=500)


def _oauth_error_page(message, status_code=400, show_login_link=False):
    """Return an HTML error page with a link back to dashboard or login."""
    msg_esc = message.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    links = '<p><a href="/login.html">Sign in with email / password</a></p><p><a href="/index.html">Return to Dashboard</a></p>'
    if not show_login_link:
        links = '<p><a href="/index.html">Return to Dashboard</a></p>'
    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Connection failed</title>
<style>body{{font-family:system-ui,sans-serif;max-width:520px;margin:60px auto;padding:24px;text-align:center;}}
.error{{color:#b91c1c;margin:16px 0;}} a{{color:#7c3aed;}} .tip{{margin-top:20px;font-size:0.95rem;color:#555;}}</style></head>
<body><h1>Connection failed</h1><p class="error">{msg_esc}</p>
{links}
<p class="tip">If you see this after &quot;Sign in with Google&quot;, your network may be blocking access to Google. Use email/password to sign in.</p></body></html>'''
    return html, status_code, {'Content-Type': 'text/html; charset=utf-8'}


def _oauth_success_page(link_flow=False, token=None, email=None, full_name=None, role=None):
    """Return HTML that redirects to dashboard. For link_flow, do not overwrite localStorage."""
    if link_flow:
        html = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Gmail connected</title></head>
<body><p>Gmail connected! Redirecting...</p>
<script>window.location.href='/index.html';</script></body></html>'''
    else:
        t = _oauth_escape_js(token)
        e = _oauth_escape_js(email)
        n = _oauth_escape_js(full_name)
        r = _oauth_escape_js(role)
        html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Login successful</title></head>
<body><p>Login successful! Redirecting...</p>
<script>
localStorage.setItem('authToken','{t}');
localStorage.setItem('userEmail','{e}');
localStorage.setItem('userRole','{r}');
localStorage.setItem('userName','{n}');
window.location.href='/index.html';
</script></body></html>'''
    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}


@app.route('/api/auth/verify', methods=['GET'])
@require_auth
def verify_token():
    """Verify authentication token."""
    try:
        return jsonify({
            'success': True,
            'user': {
                'email': request.user_email,
                'role': request.user_role
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auth/update-name', methods=['POST'])
@require_auth
def update_user_name():
    """Update user's display name."""
    try:
        data = request.json
        new_name = data.get('name', '').strip()
        
        if not new_name:
            return jsonify({
                'success': False,
                'error': 'Name cannot be empty'
            }), 400
        
        email = request.user_email
        
        # Update in USERS_DB
        if email in USERS_DB:
            USERS_DB[email]['full_name'] = new_name
        
        # Update in ACTIVE_TOKENS
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        if token in ACTIVE_TOKENS:
            ACTIVE_TOKENS[token]['full_name'] = new_name
        
        return jsonify({
            'success': True,
            'message': 'Name updated successfully',
            'full_name': new_name
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Dashboard API Endpoints
# ============================================

@app.route('/api/dashboard/stats', methods=['GET'])
@require_auth
def get_dashboard_stats():
    """Get dashboard statistics for the current user."""
    try:
        current_user = request.user_email
        dashboard = addon.get_user_dashboard(current_user)
        
        if 'error' in dashboard:
            # User doesn't exist, create user profile
            addon.setup_user_profile(current_user, current_user, 0.6, True)
            addon.add_sample_emails(current_user, count=15, phishing_ratio=0.3)
            dashboard = addon.get_user_dashboard(current_user)
        
        stats = dashboard.get('statistics', {})
        total = stats.get('total_emails_scanned') or 0
        threats = stats.get('threats_detected') or 0
        threat_rate = (threats / total * 100) if total > 0 else 0
        
        # Calculate protection score
        protection_score = 95  # Based on system configuration
        
        return jsonify({
            'success': True,
            'data': {
                'totalScanned': total,
                'threatsDetected': threats,
                'threatsBlocked': threats,  # Assuming all detected are blocked
                'threatRate': round(threat_rate, 1),
                'protectionScore': protection_score,
                'sensitivityLevel': get_sensitivity_level(dashboard['threat_threshold']),
                'autoFlagStatus': 'Enabled' if dashboard.get('auto_flag', True) else 'Disabled',
                'lastScan': format_time_ago(stats.get('last_scan')),
                'threatThreshold': dashboard.get('threat_threshold', 0.5)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/dashboard/recent-threats', methods=['GET'])
@require_auth
def get_recent_threats():
    """Get recent threats detected. Prefer live simulator list when present so dashboard matches Flagged tab."""
    try:
        current_user = request.user_email
        # Prefer live simulator list so new flags show on both dashboard and Flagged tab
        flagged = addon.gmail_simulator.get_flagged_emails(current_user)
        if flagged:
            recent = flagged[-5:] if len(flagged) > 5 else flagged
            threats = []
            for email in reversed(recent):
                score = 70
                try:
                    fr = email.get('flag_reason', '')
                    if 'score:' in fr:
                        score_str = fr.split('score:')[1].split(')')[0].strip()
                        score = int(float(score_str) * 100)
                except Exception:
                    pass
                threats.append({
                    'id': email.get('id'),
                    'subject': email.get('subject', 'No Subject'),
                    'sender': email.get('sender', 'Unknown'),
                    'score': score,
                    'time': format_time_ago(email.get('flagged_at'))
                })
            return jsonify({'success': True, 'data': threats})
        # No simulator flagged: use persisted (REAL_GMAIL_FLAGGED / disk)
        if current_user not in REAL_GMAIL_FLAGGED:
            loaded = _load_flagged_from_disk(current_user)
            if loaded:
                REAL_GMAIL_FLAGGED[current_user] = loaded
        threats = []
        if current_user in REAL_GMAIL_FLAGGED:
            raw = REAL_GMAIL_FLAGGED[current_user]
            recent = raw[-5:] if len(raw) > 5 else raw
            for email in reversed(recent):
                threats.append({
                    'id': email.get('id'),
                    'subject': email.get('subject', 'No Subject'),
                    'sender': email.get('sender', 'Unknown'),
                    'score': int(round((email.get('score') or 0) * 100)),
                    'time': email.get('time') or format_time_ago(email.get('received_at'))
                })
        return jsonify({'success': True, 'data': threats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Flagged Emails API Endpoints
# ============================================

def _sort_flagged_newest_first(emails):
    """Sort flagged email list so newest (by flagged_at or received_at) is first."""
    def sort_key(e):
        t = e.get('flagged_at') or e.get('received_at') or e.get('time') or ''
        return (t if isinstance(t, str) else str(t)) or '0'
    emails.sort(key=sort_key, reverse=True)
    return emails


def _simulator_flagged_to_api_format(flagged_list):
    """Convert simulator flagged email dicts to API response format (list of email dicts)."""
    emails = []
    for email in flagged_list:
        flag_reason = email.get('flag_reason', '')
        score = 70
        if 'score:' in flag_reason:
            try:
                score_str = flag_reason.split('score:')[1].split(')')[0].strip()
                score = int(float(score_str) * 100)
            except Exception:
                pass
        time_val = email.get('received_at', datetime.now().isoformat())
        if isinstance(time_val, str) and len(time_val) > 16:
            time_val = time_val[:16].replace('T', ' ')
        emails.append({
            'id': email.get('id'),
            'subject': email.get('subject', 'No Subject'),
            'sender': email.get('sender', 'Unknown'),
            'threatType': 'Phishing',
            'score': score,
            'time': time_val,
            'received_at': time_val,
            'flagged_at': email.get('flagged_at', ''),
            'body': (email.get('body', '') or '')[:200] + '...'
        })
    return emails


@app.route('/api/flagged-emails', methods=['GET'])
@require_auth
def get_flagged_emails():
    """Get all flagged emails for the current user. Merge live simulator list with persisted so new flags show."""
    try:
        current_user = request.user_email
        # Load from disk if not in memory (e.g. after server restart)
        if current_user not in REAL_GMAIL_FLAGGED:
            loaded = _load_flagged_from_disk(current_user)
            if loaded:
                REAL_GMAIL_FLAGGED[current_user] = loaded
        # Always get live simulator list so newly flagged emails show on Flagged tab
        simulator_flagged = addon.gmail_simulator.get_flagged_emails(current_user)
        if simulator_flagged:
            # Simulator has flagged emails: use as source of truth so Flagged tab matches dashboard
            emails = _simulator_flagged_to_api_format(simulator_flagged)
            _sort_flagged_newest_first(emails)
            # Keep persisted store in sync so we have them after restart
            if len(simulator_flagged) > len(REAL_GMAIL_FLAGGED.get(current_user, [])):
                _persist_simulator_flagged(current_user)
            return jsonify({'success': True, 'data': emails})
        # No simulator flagged: use persisted (REAL_GMAIL_FLAGGED / disk)
        if current_user in REAL_GMAIL_FLAGGED:
            raw = REAL_GMAIL_FLAGGED[current_user]
            emails = []
            for e in raw:
                score_pct = int(round((e.get('score') or 0) * 100))
                time_val = e.get('time') or e.get('received_at', '')
                if isinstance(time_val, str) and len(time_val) > 16:
                    time_val = time_val[:16].replace('T', ' ')
                received_at = e.get('received_at') or ''
                if isinstance(received_at, str) and len(received_at) > 16:
                    received_at = received_at[:16].replace('T', ' ')
                flagged_at = e.get('flagged_at') or ''
                if isinstance(flagged_at, str) and len(flagged_at) > 16:
                    flagged_at = flagged_at[:16].replace('T', ' ')
                emails.append({
                    'id': e.get('id'),
                    'subject': e.get('subject', 'No Subject'),
                    'sender': e.get('sender', 'Unknown'),
                    'threatType': (e.get('threat_type') or 'Phishing').capitalize(),
                    'score': score_pct,
                    'time': time_val,
                    'received_at': received_at or time_val,
                    'flagged_at': flagged_at,
                    'body': (e.get('body') or '')[:200] + ('...' if len(e.get('body') or '') > 200 else '')
                })
            _sort_flagged_newest_first(emails)
            return jsonify({'success': True, 'data': emails})
        return jsonify({'success': True, 'data': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/flagged-emails/<email_id>', methods=['GET'])
@require_auth
def get_email_details(email_id):
    """Get detailed information about a specific flagged email."""
    try:
        current_user = request.user_email
        # Check real Gmail flagged first
        if current_user in REAL_GMAIL_FLAGGED:
            for e in REAL_GMAIL_FLAGGED[current_user]:
                if str(e.get('id')) == str(email_id):
                    rec = e.get('received_at') or ''
                    flg = e.get('flagged_at') or ''
                    return jsonify({
                        'success': True,
                        'data': {
                            'id': e.get('id'),
                            'subject': e.get('subject', 'No Subject'),
                            'sender': e.get('sender', 'Unknown'),
                            'body': e.get('body', ''),
                            'threatScore': int(round((e.get('score') or 0) * 100)),
                            'threatType': (e.get('threat_type') or 'phishing').capitalize(),
                            'riskFactors': e.get('risk_factors', []),
                            'recommendations': e.get('recommendations', []),
                            'confidence': 'medium',
                            'received_at': rec,
                            'flagged_at': flg,
                            'riskBreakdown': e.get('risk_breakdown'),
                            'suspiciousSpans': e.get('suspicious_spans', []),
                            'suspiciousUrls': e.get('suspicious_urls', []),
                            'featureContributions': e.get('feature_contributions', []),
                        }
                    })
        # Fallback: simulator inbox + analyze
        inbox = addon.gmail_simulator.get_inbox(current_user)
        email = None
        for e in inbox:
            if str(e.get('id')) == str(email_id):
                email = e
                break
        if not email:
            return jsonify({'success': False, 'error': 'Email not found'}), 404
        result = addon.analyze_single_email(current_user, email)
        return jsonify({
            'success': True,
            'data': {
                'id': email['id'],
                'subject': email.get('subject', 'No Subject'),
                'sender': email.get('sender', 'Unknown'),
                'body': email.get('body', ''),
                'threatScore': int(result.get('threat_score', 0) * 100),
                'threatType': result.get('threat_type', 'unknown'),
                'riskFactors': result.get('risk_factors', []),
                'recommendations': result.get('recommendations', []),
                'confidence': result.get('confidence', 'medium'),
                'riskBreakdown': result.get('risk_breakdown'),
                'suspiciousSpans': result.get('suspicious_spans', []),
                'suspiciousUrls': result.get('suspicious_urls', []),
                'featureContributions': result.get('feature_contributions', []),
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/flagged-emails/<email_id>', methods=['DELETE'])
@require_auth
def delete_email(email_id):
    """Delete a flagged email."""
    try:
        # In a real implementation, you'd delete from the inbox
        return jsonify({
            'success': True,
            'message': 'Email deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Scan API Endpoints
# ============================================

def _extract_urls_from_body(text):
    """Extract URLs from email body for ML/NLP threat detection."""
    if not text:
        return []
    url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+'
    return list(set(re.findall(url_pattern, text)))


def _scan_inbox_simulator_result(current_user):
    """Run simulator scan and optionally seed if empty. Returns (result_dict, error_str or None)."""
    result = addon.scan_inbox(current_user, auto_flag=True)
    if result.get('error'):
        return None, result['error']
    if result.get('total_scanned', 0) == 0:
        addon.add_sample_emails(current_user, count=15, phishing_ratio=0.4)
        result = addon.scan_inbox(current_user, auto_flag=True)
        if result.get('error'):
            return None, result['error']
    return result, None


def _persist_simulator_flagged(current_user):
    """Save simulator flagged emails to REAL_GMAIL_FLAGGED and disk so Flagged Emails page shows them."""
    flagged = addon.gmail_simulator.get_flagged_emails(current_user)
    now_iso = datetime.now().isoformat()
    records = []
    for email in flagged:
        flag_reason = email.get('flag_reason', '')
        score = 0.7
        if 'score:' in flag_reason:
            try:
                score = float(flag_reason.split('score:')[1].split(')')[0].strip())
            except Exception:
                pass
        received_at = email.get('received_at', now_iso)
        time_str = received_at[:16].replace('T', ' ') if isinstance(received_at, str) and len(received_at) > 16 else str(received_at)[:16]
        flagged_at = email.get('flagged_at', now_iso)
        records.append({
            'id': email.get('id'),
            'subject': email.get('subject', 'No Subject'),
            'sender': email.get('sender', 'Unknown'),
            'body': (email.get('body') or '')[:500],
            'threat_type': 'Phishing',
            'score': score,
            'time': time_str,
            'received_at': received_at,
            'flagged_at': flagged_at,
            'risk_factors': [],
            'recommendations': [],
        })
    REAL_GMAIL_FLAGGED[current_user] = records
    _save_flagged_to_disk(current_user, records)


@app.route('/api/scan/inbox', methods=['POST'])
@require_auth
def scan_inbox():
    """Scan the user's inbox for threats (real Gmail if connected, else simulated)."""
    try:
        current_user = request.user_email
        refresh_token = USERS_DB.get(current_user, {}).get('gmail_refresh_token')
        print(f"\n[SCAN] user={current_user} has_refresh_token={bool(refresh_token)}")

        if refresh_token:
            # Real Gmail scan: fetch from Gmail API, run ML/NLP threat detection
            from gmail_client import GmailClient
            client = GmailClient('gmail_config.json')
            try:
                client.authenticate_with_token(refresh_token)
            except Exception as e:
                print(f"[SCAN] Gmail auth failed: {e}, falling back to simulator")
                result, err = _scan_inbox_simulator_result(current_user)
                if err:
                    return jsonify({'success': False, 'error': f'Gmail auth failed. {err}'}), 400
                _persist_simulator_flagged(current_user)
                return jsonify({
                    'success': True,
                    'data': {
                        'totalScanned': result['total_scanned'],
                        'threatsFound': result['threats_found'],
                        'threatRate': result['threat_rate'] * 100,
                        'source': 'simulated',
                        'fallbackReason': 'Gmail sign-in expired or was revoked. Connect Gmail again in Settings to scan your real inbox.'
                    }
                })
            try:
                raw_messages = client.get_messages(max_results=100)
            except Exception as e:
                err_str = str(e).lower()
                is_permission_error = (
                    '403' in err_str or 'permitted' in err_str or 'insufficient' in err_str
                    or 'forbidden' in err_str or 'access not configured' in err_str
                    or 'not been used' in err_str or 'disabled' in err_str
                )
                print(f"[SCAN] Gmail API error: {e}, fallback to simulator (is_permission_error={is_permission_error})")
                result, err = _scan_inbox_simulator_result(current_user)
                if err:
                    return jsonify({
                        'success': False,
                        'error': 'Gmail access was denied or not enabled. Enable Gmail API at: https://console.cloud.google.com/apis/library/gmail.googleapis.com'
                    }), 403
                _persist_simulator_flagged(current_user)
                return jsonify({
                    'success': True,
                    'data': {
                        'totalScanned': result['total_scanned'],
                        'threatsFound': result['threats_found'],
                        'threatRate': result['threat_rate'] * 100,
                        'source': 'simulated',
                        'fallbackReason': 'Gmail could not be accessed (permission or API not enabled). Scanned sample inbox instead. Connect Gmail in Settings to scan your real inbox.'
                    }
                })
            print(f"[SCAN] Gmail returned {len(raw_messages)} messages")
            profile = addon.addon_manager.get_profile(current_user)
            if not profile:
                addon.setup_user_profile(current_user, current_user, 0.5, True)
                profile = addon.addon_manager.get_profile(current_user)
            threat_threshold = (profile or {}).get('addon_config', {}).get('threat_threshold', 0.6)
            threat_threshold = min(threat_threshold, 0.45)  # lower so spam is caught (was 0.6)

            existing_flagged = _load_flagged_from_disk(current_user)
            existing_ids = {str(e.get('id')) for e in existing_flagged}
            new_flagged_this_scan = []
            total_scanned = len(raw_messages)
            threats_found = 0
            now_iso = datetime.now().isoformat()

            for i, msg in enumerate(raw_messages):
                body = msg.get('body', '') or msg.get('snippet', '')
                subject = msg.get('subject', '')
                text_for_analysis = f"{subject}\n\n{body}".strip() or body or subject
                email_data = {
                    'subject': subject,
                    'body': text_for_analysis,
                    'sender': msg.get('sender', ''),
                    'sender_name': msg.get('sender_name', ''),
                    'urls': _extract_urls_from_body(text_for_analysis),
                }
                analysis = addon.threat_detector.analyze_email(email_data)
                score = analysis['threat_score']
                if i < 5:
                    print(f"[SCAN] msg {i+1} score={score:.2f} subj={subject[:50]!r}")
                if score >= threat_threshold:
                    threats_found += 1
                    received = msg.get('received_at', datetime.now().isoformat())
                    if isinstance(received, str) and 'T' in received:
                        try:
                            dt = datetime.fromisoformat(received.replace('Z', '+00:00'))
                            time_str = dt.strftime('%Y-%m-%d %H:%M')
                        except Exception:
                            time_str = received[:16] if len(received) >= 16 else received
                    else:
                        time_str = str(received)[:16]
                    msg_id = str(msg.get('id') or msg.get('gmail_message_id', ''))
                    record = {
                        'id': msg_id,
                        'subject': msg.get('subject', 'No Subject'),
                        'sender': msg.get('sender', 'Unknown'),
                        'body': (body or '')[:500],
                        'threat_type': analysis.get('threat_type', 'phishing').capitalize(),
                        'score': analysis['threat_score'],
                        'time': time_str,
                        'received_at': received,
                        'flagged_at': now_iso,
                        'risk_factors': analysis.get('risk_factors', []),
                        'recommendations': analysis.get('recommendations', []),
                        'risk_breakdown': analysis.get('risk_breakdown'),
                        'suspicious_spans': analysis.get('suspicious_spans', []),
                        'suspicious_urls': analysis.get('suspicious_urls', []),
                        'feature_contributions': analysis.get('feature_contributions', []),
                    }
                    new_flagged_this_scan.append(record)
                    if msg_id not in existing_ids:
                        existing_flagged.append(record)
                        existing_ids.add(msg_id)

            REAL_GMAIL_FLAGGED[current_user] = existing_flagged
            _save_flagged_to_disk(current_user, existing_flagged)

            if profile:
                addon.addon_manager.update_statistics(
                    current_user, scanned=total_scanned, threats=threats_found
                )
            threat_rate = (threats_found / total_scanned * 100) if total_scanned else 0
            return jsonify({
                'success': True,
                'data': {
                    'totalScanned': total_scanned,
                    'threatsFound': threats_found,
                    'threatRate': round(threat_rate, 1),
                    'source': 'gmail'
                }
            })

        # No Gmail token: use simulator + ML/NLP (existing flow)
        print(f"[SCAN] Using simulator (no refresh token)")
        result, err = _scan_inbox_simulator_result(current_user)
        if err:
            print(f"[SCAN] Simulator error: {err}")
            return jsonify({'success': False, 'error': err}), 400
        print(f"[SCAN] Simulator: scanned={result.get('total_scanned', 0)} threats={result.get('threats_found', 0)}")
        _persist_simulator_flagged(current_user)
        return jsonify({
            'success': True,
            'data': {
                'totalScanned': result['total_scanned'],
                'threatsFound': result['threats_found'],
                'threatRate': result['threat_rate'] * 100,
                'source': 'simulated'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scan/email', methods=['POST'])
@require_auth
def scan_single_email():
    """Scan a single email."""
    try:
        current_user = request.user_email
        email_data = request.json
        result = addon.analyze_single_email(current_user, email_data)
        
        return jsonify({
            'success': True,
            'data': {
                'isThreat': result['is_threat'],
                'threatScore': result['threat_score'] * 100,
                'threatType': result.get('threat_type', 'unknown'),
                'riskFactors': result.get('risk_factors', []),
                'recommendations': result.get('recommendations', [])
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Reports API Endpoints
# ============================================

@app.route('/api/reports/summary', methods=['GET'])
@require_auth
def get_report_summary():
    """Get report summary."""
    try:
        current_user = request.user_email
        dashboard = addon.get_user_dashboard(current_user)
        
        # Get all emails to categorize
        inbox = addon.gmail_simulator.get_inbox(current_user)
        flagged = addon.gmail_simulator.get_flagged_emails(current_user)
        
        stats = dashboard['statistics']
        total = stats['total_emails_scanned']
        threats = stats['threats_detected']
        
        # Estimate categories
        phishing = int(threats * 0.7)  # 70% phishing
        spam = threats - phishing  # Rest is spam
        clean = total - threats
        
        return jsonify({
            'success': True,
            'data': {
                'totalEmails': total,
                'phishing': phishing,
                'spam': spam,
                'clean': clean
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reports/activity', methods=['GET'])
@require_auth
def get_activity_timeline():
    """Get activity timeline."""
    try:
        # Generate activity log based on user actions
        activities = [
            {
                'time': '2 minutes ago',
                'text': 'Completed inbox scan'
            },
            {
                'time': '15 minutes ago',
                'text': 'Flagged suspicious email'
            },
            {
                'time': '1 hour ago',
                'text': 'Updated threat settings'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': activities
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Whitelist/Blacklist API Endpoints
# ============================================

@app.route('/api/whitelist', methods=['GET'])
@require_auth
def get_whitelist():
    """Get whitelist."""
    try:
        current_user = request.user_email
        profile = addon.addon_manager.get_profile(current_user)
        whitelist = profile['addon_config']['whitelist'] if profile else []
        
        return jsonify({
            'success': True,
            'data': whitelist
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/whitelist', methods=['POST'])
@require_auth
def add_to_whitelist():
    """Add email to whitelist."""
    try:
        current_user = request.user_email
        email = request.json.get('email')
        addon.add_to_whitelist(current_user, email)
        
        return jsonify({
            'success': True,
            'message': f'Added {email} to whitelist'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/whitelist/<email>', methods=['DELETE'])
@require_auth
def remove_from_whitelist(email):
    """Remove email from whitelist."""
    try:
        current_user = request.user_email
        profile = addon.addon_manager.get_profile(current_user)
        if profile and email in profile['addon_config']['whitelist']:
            profile['addon_config']['whitelist'].remove(email)
            addon.addon_manager._save_profile(CURRENT_USER)
        
        return jsonify({
            'success': True,
            'message': f'Removed {email} from whitelist'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/blacklist', methods=['GET'])
@require_auth
def get_blacklist():
    """Get blacklist."""
    try:
        current_user = request.user_email
        profile = addon.addon_manager.get_profile(current_user)
        blacklist = profile['addon_config']['blacklist'] if profile else []
        
        return jsonify({
            'success': True,
            'data': blacklist
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/blacklist', methods=['POST'])
@require_auth
def add_to_blacklist():
    """Add email to blacklist."""
    try:
        current_user = request.user_email
        email = request.json.get('email')
        addon.add_to_blacklist(current_user, email)
        
        return jsonify({
            'success': True,
            'message': f'Added {email} to blacklist'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/blacklist/<email>', methods=['DELETE'])
@require_auth
def remove_from_blacklist(email):
    """Remove email from blacklist."""
    try:
        current_user = request.user_email
        profile = addon.addon_manager.get_profile(current_user)
        if profile and email in profile['addon_config']['blacklist']:
            profile['addon_config']['blacklist'].remove(email)
            addon.addon_manager._save_profile(CURRENT_USER)
        
        return jsonify({
            'success': True,
            'message': f'Removed {email} from blacklist'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Settings API Endpoints
# ============================================

@app.route('/api/settings', methods=['GET'])
@require_auth
def get_settings():
    """Get user settings."""
    try:
        current_user = request.user_email
        dashboard = addon.get_user_dashboard(current_user)
        
        gmail_connected = USERS_DB.get(current_user, {}).get('gmail_connected', False)
        member_since = EMAIL_MEMBER_SINCE.get(current_user) or format_member_since(USERS_DB.get(current_user, {}).get('created_at')) or '—'
        return jsonify({
            'success': True,
            'data': {
                'username': current_user.split('@')[0],
                'email': current_user,
                'threatThreshold': dashboard['threat_threshold'],
                'autoFlag': dashboard.get('auto_flag', True),
                'notifications': True,
                'memberSince': member_since,
                'gmailConnected': gmail_connected
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/settings', methods=['PUT'])
@require_auth
def update_settings():
    """Update user settings."""
    try:
        current_user = request.user_email
        settings = request.json
        
        # Update settings in addon
        addon.update_addon_settings(
            current_user,
            threat_threshold=settings.get('threatThreshold', 0.6),
            auto_flag=settings.get('autoFlag', True),
            notifications=settings.get('notifications', True)
        )
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Health check (for Render / load balancers)
# ============================================

@app.route('/health')
def health():
    """Return 200 so Render knows the service is up."""
    return jsonify({'status': 'ok', 'service': 'mailthreat-analyzer'}), 200


# ============================================
# Serve Static Files (must be last so /api/* routes match first)
# ============================================

@app.route('/')
def index():
    """Serve the main HTML file."""
    return send_from_directory('web_ui', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, images)."""
    return send_from_directory('web_ui', path)


# ============================================
# Utility Functions
# ============================================

def get_sensitivity_level(threshold):
    """Convert threshold to sensitivity level."""
    if threshold <= 0.3:
        return 'Very High'
    elif threshold <= 0.5:
        return 'High'
    elif threshold <= 0.7:
        return 'Medium'
    else:
        return 'Low'


def format_time_ago(iso_time):
    """Format ISO time to 'X ago' format."""
    if not iso_time:
        return 'Never'
    
    try:
        time = datetime.fromisoformat(iso_time)
        now = datetime.now()
        diff = now - time
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return 'Just now'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours} hour{"s" if hours > 1 else ""} ago'
        else:
            days = int(seconds / 86400)
            return f'{days} day{"s" if days > 1 else ""} ago'
    except:
        return 'Recently'


# ============================================
# Main
# ============================================

if __name__ == '__main__':
    print("="*60)
    print("🚀 MailThreat Analyzer - Web Server")
    print("="*60)
    print()
    print("Starting server...")
    print()
    
    # Setup demo users with sample data
    print("Setting up demo users...")
    for email in USERS_DB.keys():
        try:
            profile = addon.addon_manager.get_profile(email)
            if not profile:
                addon.setup_user_profile(email, email, 0.6, True)
                addon.add_sample_emails(email, count=15, phishing_ratio=0.3)
        except:
            addon.setup_user_profile(email, email, 0.6, True)
            addon.add_sample_emails(email, count=15, phishing_ratio=0.3)
    print("✓ Demo users created with sample data")
    
    print()
    print("✓ Server ready!")
    print()
    print("📱 Open your browser and go to:")
    print("   http://localhost:5001/login.html")
    print()
    print("Demo Accounts:")
    print("   CEO:      demo@example.com / demo123")
    print("   Employee: employee@example.com / employee123")
    print()
    print("Press Ctrl+C to stop the server")
    print("="*60)
    print()
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
