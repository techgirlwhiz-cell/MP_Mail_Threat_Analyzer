// ============================================
// MailThreat Analyzer - Login Page
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    setupLoginEventListeners();
    checkExistingSession();
});

function setupLoginEventListeners() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    const googleLoginBtn = document.getElementById('googleLoginBtn');
    if (googleLoginBtn) {
        googleLoginBtn.addEventListener('click', handleGoogleLogin);
    }

    const togglePasswordBtn = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    const togglePasswordIcon = document.getElementById('togglePasswordIcon');
    if (togglePasswordBtn && passwordInput && togglePasswordIcon) {
        togglePasswordBtn.addEventListener('click', function() {
            var isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            togglePasswordIcon.classList.toggle('fa-eye', !isPassword);
            togglePasswordIcon.classList.toggle('fa-eye-slash', isPassword);
            togglePasswordBtn.setAttribute('title', isPassword ? 'Hide password' : 'Show password');
            togglePasswordBtn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
        });
    }
}

function checkExistingSession() {
    // Check if user is already logged in
    const token = localStorage.getItem('authToken');
    if (token) {
        // Redirect to dashboard
        window.location.href = '/index.html';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const submitBtn = document.querySelector('.btn-login');
    const email = (emailInput && emailInput.value) ? emailInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value : '';
    const rememberMe = document.getElementById('rememberMe') ? document.getElementById('rememberMe').checked : false;
    
    if (!email || !password) {
        showError('Please enter email and password.');
        return;
    }
    
    showLoading();
    hideError();
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.setAttribute('aria-busy', 'true');
    }
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, rememberMe })
        });
        
        var data;
        var contentType = response.headers.get('Content-Type') || '';
        if (contentType.indexOf('application/json') !== -1) {
            data = await response.json();
        } else {
            var text = await response.text();
            if (response.ok) {
                showError('Invalid response from server. Try again.');
            } else {
                showError('Sign in failed. Is the server running? Use demo@example.com / demo123 to test.');
            }
            return;
        }
        
        if (data && data.success) {
            localStorage.setItem('authToken', data.token);
            localStorage.setItem('userEmail', data.user.email);
            localStorage.setItem('userRole', data.user.role || 'employee');
            localStorage.setItem('userName', data.user.full_name || data.user.email.split('@')[0]);
            if (data.user.is_first_login) {
                localStorage.setItem('needsNameSetup', 'true');
            }
            if (data.user.gmail_connected === false) {
                window.location.href = '/index.html?connect_gmail=1';
                return;
            }
            window.location.href = '/index.html';
        } else {
            showError(data && data.error ? data.error : 'Invalid email or password.');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Sign in failed. Check the server is running and try again.');
    } finally {
        hideLoading();
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.removeAttribute('aria-busy');
        }
    }
}

async function handleGoogleLogin() {
    showLoading();
    hideError();
    
    try {
        // Get Google OAuth URL
        const response = await fetch('/api/auth/google/url');
        const data = await response.json();
        
        if (data.success) {
            // Store state for verification
            sessionStorage.setItem('oauth_state', data.state);
            // Redirect to Google OAuth
            window.location.href = data.url;
        } else {
            showError(data.error || 'Google login not available');
            hideLoading();
        }
    } catch (error) {
        console.error('Google login error:', error);
        showError('Google login failed. Please check your connection.');
        hideLoading();
    }
}

function showLoading() {
    document.getElementById('loginLoading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loginLoading').classList.add('hidden');
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    document.getElementById('errorMessage').classList.add('hidden');
}

console.log('✅ Login page loaded');
