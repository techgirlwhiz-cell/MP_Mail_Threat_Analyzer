// ============================================
// Email Threat Protection Dashboard
// Main JavaScript Application
// ============================================

// Configuration
const CONFIG = {
    apiEndpoint: '/api',
    refreshInterval: 30000 // 30 seconds
};

// Application State
const appState = {
    currentPage: 'dashboard',
    userProfile: null,
    flaggedEmails: [],
    recentThreats: [],
    statistics: {},
    refreshTimer: null,
    authToken: null,
    userEmail: null,
    userRole: null,
    userName: null
};

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    checkAuthentication();
});

function checkAuthentication() {
    // Check if user is logged in
    const token = localStorage.getItem('authToken');
    const email = localStorage.getItem('userEmail');
    const role = localStorage.getItem('userRole');
    const name = localStorage.getItem('userName');
    
    if (!token || !email) {
        // Redirect to login page
        window.location.href = '/login.html';
        return;
    }
    
    // Store auth info
    appState.authToken = token;
    appState.userEmail = email;
    appState.userRole = role || 'employee';
    appState.userName = name || email.split('@')[0];
    
    // Initialize app
    initializeApp();
    setupEventListeners();
    loadUserProfile().then(function() {
        maybeShowConnectGmailModal();
    });
    loadDashboardData();
}

function getUrlParam(name) {
    var params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function maybeShowConnectGmailModal() {
    if (getUrlParam('connect_gmail') !== '1') return;
    var profile = appState.userProfile || {};
    if (profile.gmailConnected) {
        if (window.history.replaceState) window.history.replaceState({}, '', window.location.pathname);
        return;
    }
    var overlay = document.getElementById('connectGmailOverlay');
    if (overlay) overlay.classList.remove('hidden');
}

function closeConnectGmailModal() {
    var overlay = document.getElementById('connectGmailOverlay');
    if (overlay) overlay.classList.add('hidden');
    if (window.history.replaceState) window.history.replaceState({}, '', window.location.pathname);
}

function initializeApp() {
    console.log('🚀 Email Threat Protection Dashboard Initialized');
    
    // Apply saved theme (light/dark)
    var savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
    
    // Set user info from auth
    document.getElementById('userName').textContent = appState.userName;
    document.getElementById('userEmail').textContent = appState.userEmail;
    
    // Check if user needs to set up their name
    if (localStorage.getItem('needsNameSetup') === 'true') {
        promptForName();
    }
    
    // Start auto-refresh
    startAutoRefresh();
}

function promptForName() {
    const currentName = appState.userName;
    const customName = prompt(
        `Welcome! Your display name is currently "${currentName}".\n\nWould you like to change it? (Click Cancel to keep it)`,
        currentName
    );
    
    if (customName && customName.trim() !== '' && customName.trim() !== currentName) {
        updateUserName(customName.trim());
    }
    
    // Remove the flag
    localStorage.removeItem('needsNameSetup');
}

async function updateUserName(newName) {
    try {
        const response = await apiCall('/auth/update-name', 'POST', { name: newName });
        
        if (response && response.success) {
            appState.userName = newName;
            localStorage.setItem('userName', newName);
            document.getElementById('userName').textContent = newName;
            showToast('Name updated successfully!', 'success');
        } else {
            showToast('Failed to update name', 'error');
        }
    } catch (error) {
        console.error('Name update error:', error);
        showToast('Failed to update name', 'error');
    }
}

// ============================================
// Event Listeners
// ============================================

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', handleNavigation);
    });
    
    // Sidebar profile block: click to go to Profile page
    const userProfileLink = document.getElementById('userProfileLink');
    if (userProfileLink) {
        userProfileLink.addEventListener('click', function(e) {
            e.preventDefault();
            navigateToPage('profile');
        });
    }
    
    // Theme toggle (Profile page)
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('change', handleThemeToggle);
    }
    
    // Save Profile button
    const saveProfileBtn = document.getElementById('saveProfileBtn');
    if (saveProfileBtn) {
        saveProfileBtn.addEventListener('click', handleSaveProfile);
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
        console.log('✅ Logout button event listener attached');
    } else {
        console.error('❌ Logout button not found!');
    }
    
    // Scan Now button
    const scanNowBtn = document.getElementById('scanNowBtn');
    if (scanNowBtn) {
        scanNowBtn.addEventListener('click', handleScanNow);
        console.log('✅ Scan Now button event listener attached');
    } else {
        console.error('❌ Scan Now button not found!');
    }
    
    // Notification icon (bell) - go to dashboard and refresh recent threats
    const notificationIcon = document.querySelector('.notification-icon');
    if (notificationIcon) {
        notificationIcon.addEventListener('click', function() {
            var pageId = 'dashboard';
            document.querySelectorAll('.nav-item').forEach(function(item) {
                item.classList.toggle('active', item.dataset.page === pageId);
            });
            document.querySelectorAll('.page-content').forEach(function(page) {
                page.classList.add('hidden');
            });
            var target = document.getElementById(pageId + 'Page');
            if (target) {
                target.classList.remove('hidden');
                appState.currentPage = pageId;
                updatePageTitle(pageId);
            }
            loadDashboardData().then(function() {
                var el = document.getElementById('recentThreatsList');
                if (el) el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            });
        });
        notificationIcon.style.cursor = 'pointer';
        notificationIcon.setAttribute('title', 'View recent threats');
    }

    // Connect Gmail button (dashboard settings)
    const connectGmailBtn = document.getElementById('connectGmailBtn');
    if (connectGmailBtn) {
        connectGmailBtn.addEventListener('click', handleConnectGmail);
    }
    // Connect Gmail modal (after email login)
    const connectGmailModalBtn = document.getElementById('connectGmailModalBtn');
    if (connectGmailModalBtn) {
        connectGmailModalBtn.addEventListener('click', handleConnectGmail);
    }
    const connectGmailSkipBtn = document.getElementById('connectGmailSkipBtn');
    if (connectGmailSkipBtn) {
        connectGmailSkipBtn.addEventListener('click', closeConnectGmailModal);
    }
    
    // Keyboard shortcut: Ctrl+S / Cmd+S to run Scan
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            if (document.getElementById('scanNowBtn')) handleScanNow();
        }
    });

    // Change Name button
    const changeNameBtn = document.getElementById('changeNameBtn');
    if (changeNameBtn) {
        changeNameBtn.addEventListener('click', handleChangeName);
    }
    
    // Settings controls
    const threatThreshold = document.getElementById('threatThreshold');
    if (threatThreshold) {
        threatThreshold.addEventListener('input', function() {
            document.getElementById('thresholdValue').textContent = this.value + '%';
        });
    }
    
    // Save Settings button
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', handleSaveSettings);
    }
    
    // Add Whitelist button
    const addWhitelistBtn = document.getElementById('addWhitelistBtn');
    if (addWhitelistBtn) {
        addWhitelistBtn.addEventListener('click', openAddWhitelistModal);
    }
    
    // Add Blacklist button
    const addBlacklistBtn = document.getElementById('addBlacklistBtn');
    if (addBlacklistBtn) {
        addBlacklistBtn.addEventListener('click', openAddBlacklistModal);
    }
    
    // Modal close
    const closeModal = document.getElementById('closeModal');
    if (closeModal) {
        closeModal.addEventListener('click', closeEmailModal);
    }
    
    // Click outside modal to close
    document.getElementById('emailModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeEmailModal();
        }
    });
    
    // Click outside add modals to close
    const addWhitelistModal = document.getElementById('addWhitelistModal');
    if (addWhitelistModal) {
        addWhitelistModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeAddWhitelistModal();
            }
        });
    }
    
    const addBlacklistModal = document.getElementById('addBlacklistModal');
    if (addBlacklistModal) {
        addBlacklistModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeAddBlacklistModal();
            }
        });
    }
    
    // Filter and search
    const threatFilter = document.getElementById('threatFilter');
    if (threatFilter) {
        threatFilter.addEventListener('change', handleFilterChange);
    }
    
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
}

// ============================================
// Navigation
// ============================================

function handleNavigation(e) {
    e.preventDefault();
    
    const pageId = this.dataset.page;
    
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    this.classList.add('active');
    
    // Hide all pages
    document.querySelectorAll('.page-content').forEach(page => {
        page.classList.add('hidden');
    });
    
    // Show selected page
    const targetPage = document.getElementById(pageId + 'Page');
    if (targetPage) {
        targetPage.classList.remove('hidden');
        appState.currentPage = pageId;
        
        // Update page title
        updatePageTitle(pageId);
        
        // Load page-specific data
        loadPageData(pageId);
    }
}

function updatePageTitle(pageId) {
    const titles = {
        'dashboard': 'Dashboard',
        'flagged': 'Flagged Emails',
        'reports': 'Reports',
        'whitelist': 'Whitelist & Blacklist',
        'settings': 'Settings',
        'profile': 'Profile',
        'scanHistory': 'Scan History',
        'securityTips': 'Security Tips'
    };
    
    document.getElementById('pageTitle').textContent = titles[pageId] || 'Dashboard';
}

function navigateToPage(pageId) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === pageId);
    });
    document.querySelectorAll('.page-content').forEach(page => page.classList.add('hidden'));
    const target = document.getElementById(pageId + 'Page');
    if (target) {
        target.classList.remove('hidden');
        appState.currentPage = pageId;
        updatePageTitle(pageId);
        loadPageData(pageId);
    }
}

// ============================================
// Data Loading Functions
// ============================================

async function loadUserProfile() {
    try {
        const response = await apiCall('/settings', 'GET');
        
        if (response && response.success) {
            appState.userProfile = response.data;
            updateUserProfile(response.data);
        } else {
            // Fallback to stored data
            const mockProfile = {
                username: appState.userEmail.split('@')[0],
                email: appState.userEmail,
                memberSince: '—',
                threatThreshold: 0.6,
                autoFlag: true,
                notifications: true,
                gmailConnected: false
            };
            appState.userProfile = mockProfile;
            updateUserProfile(mockProfile);
        }
    } catch (error) {
        console.error('Failed to load user profile:', error);
        // Use fallback
        const mockProfile = {
            username: appState.userEmail.split('@')[0],
            email: appState.userEmail,
            memberSince: '—',
            threatThreshold: 0.6,
            autoFlag: true,
            notifications: true,
            gmailConnected: false
        };
        appState.userProfile = mockProfile;
        updateUserProfile(mockProfile);
    }
}

function updateUserProfile(profile) {
    var displayNameEl = document.getElementById('settingsDisplayName');
    if (displayNameEl) displayNameEl.textContent = appState.userName;
    var emailEl = document.getElementById('settingsEmail');
    if (emailEl) emailEl.textContent = profile.email;
    var memberEl = document.getElementById('memberSince');
    if (memberEl) memberEl.textContent = profile.memberSince || '—';

    // Update Gmail connection status on dashboard
    var statusCard = document.getElementById('gmailStatusCard');
    var statusText = document.getElementById('gmailStatusText');
    if (statusCard && statusText) {
        if (profile.gmailConnected) {
            statusCard.classList.add('connected');
            statusCard.classList.remove('not-connected');
            statusText.textContent = 'Gmail connected';
        } else {
            statusCard.classList.add('not-connected');
            statusCard.classList.remove('connected');
            statusText.textContent = 'Connect Gmail to scan inbox';
        }
    }
    
    // Update settings controls
    const thresholdSlider = document.getElementById('threatThreshold');
    if (thresholdSlider) {
        thresholdSlider.value = (profile.threatThreshold != null ? profile.threatThreshold : 0.6) * 100;
        var thresholdVal = document.getElementById('thresholdValue');
        if (thresholdVal) thresholdVal.textContent = Math.round((profile.threatThreshold != null ? profile.threatThreshold : 0.6) * 100) + '%';
    }
    
    var autoFlag = document.getElementById('autoFlag');
    if (autoFlag) autoFlag.checked = profile.autoFlag !== false;
    var notifications = document.getElementById('notifications');
    if (notifications) notifications.checked = profile.notifications !== false;
}

async function loadDashboardData() {
    try {
        const response = await apiCall('/dashboard/stats', 'GET');
        
        if (response && response.success) {
            appState.statistics = response.data;
            updateDashboardStats(response.data);
        } else {
            console.error('Failed to load dashboard stats');
        }
        
        // Load recent threats
        await loadRecentThreats();
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

function updateDashboardStats(stats) {
    const totalScannedEl = document.getElementById('totalScanned');
    const threatsDetectedEl = document.getElementById('threatsDetected');
    const threatsBlockedEl = document.getElementById('threatsBlocked');
    const threatRateEl = document.getElementById('threatRate');
    if (totalScannedEl) totalScannedEl.textContent = Number(stats.totalScanned || 0).toLocaleString();
    if (threatsDetectedEl) threatsDetectedEl.textContent = Number(stats.threatsDetected || 0).toLocaleString();
    if (threatsBlockedEl) threatsBlockedEl.textContent = Number(stats.threatsBlocked || 0).toLocaleString();
    if (threatRateEl) threatRateEl.textContent = (stats.threatRate != null ? stats.threatRate : 0) + '%';

    document.getElementById('protectionScore').textContent = (stats.protectionScore != null ? stats.protectionScore : 95) + '%';
    document.getElementById('sensitivityLevel').textContent = stats.sensitivityLevel || 'Medium';
    document.getElementById('autoFlagStatus').textContent = stats.autoFlagStatus || 'Enabled';
    document.getElementById('lastScanTime').textContent = stats.lastScan || 'Never';

    updateProtectionCircle(stats.protectionScore != null ? stats.protectionScore : 95);
}

function updateProtectionCircle(score) {
    const circle = document.getElementById('protectionCircle');
    const circumference = 2 * Math.PI * 80;
    const offset = circumference - (score / 100) * circumference;
    
    if (circle) {
        circle.style.strokeDashoffset = offset;
    }
}

async function loadRecentThreats() {
    try {
        const response = await apiCall('/dashboard/recent-threats', 'GET');
        const threats = (response && response.success && Array.isArray(response.data)) ? response.data : [];
        displayRecentThreats(threats);
        updateNotificationBadge(threats.length);
    } catch (error) {
        console.error('Failed to load recent threats:', error);
        displayRecentThreats([]);
        updateNotificationBadge(0);
    }
}

function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        badge.textContent = String(count);
        badge.style.display = '';
    }
}

function displayRecentThreats(threats) {
    appState.recentThreats = threats || [];
    const container = document.getElementById('recentThreatsList');
    
    if (!threats || threats.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-gray);">No recent threats detected</p>';
        return;
    }
    
    const threatOnclick = (t) => typeof t.id === 'string' ? `openEmailModal('${String(t.id).replace(/'/g, "\\'")}')` : `openEmailModal(${t.id})`;
    container.innerHTML = threats.map(threat => `
        <div class="threat-item" onclick="${threatOnclick(threat)}">
            <div class="threat-icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="threat-info">
                <div class="threat-subject">${escapeHtml(threat.subject)}</div>
                <div class="threat-sender">${escapeHtml(threat.sender)}</div>
            </div>
            <div class="threat-score">
                <div class="threat-percentage">${threat.score}%</div>
                <div class="threat-label">Risk</div>
            </div>
        </div>
    `).join('');
}

function loadPageData(pageId) {
    switch(pageId) {
        case 'flagged':
            loadFlaggedEmails();
            break;
        case 'reports':
            loadReports();
            break;
        case 'whitelist':
            loadWhitelist();
            loadBlacklist();
            break;
        case 'profile':
            loadProfilePage();
            break;
        case 'scanHistory':
            loadScanHistory();
            break;
        case 'securityTips':
            break;
    }
}

function loadProfilePage() {
    document.getElementById('profileDisplayName').value = appState.userName || '';
    document.getElementById('profileEmail').textContent = appState.userEmail || '—';
    var memberSince = (appState.userProfile && appState.userProfile.memberSince) || document.getElementById('memberSince').textContent || '—';
    document.getElementById('profileMemberSince').textContent = memberSince;
    var isDark = (localStorage.getItem('theme') || 'light') === 'dark';
    var themeToggleEl = document.getElementById('themeToggle');
    var themeLabelEl = document.getElementById('themeLabel');
    if (themeToggleEl) themeToggleEl.checked = isDark;
    if (themeLabelEl) themeLabelEl.textContent = isDark ? 'Dark mode' : 'Light mode';
}

function handleThemeToggle() {
    var isDark = document.getElementById('themeToggle').checked;
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    applyTheme(isDark ? 'dark' : 'light');
    var themeLabel = document.getElementById('themeLabel');
    if (themeLabel) themeLabel.textContent = isDark ? 'Dark mode' : 'Light mode';
}

function applyTheme(theme) {
    var root = document.documentElement;
    if (theme === 'dark') {
        root.setAttribute('data-theme', 'dark');
    } else {
        root.removeAttribute('data-theme');
    }
}

function loadScanHistory() {
    var tbody = document.getElementById('scanHistoryBody');
    var emptyEl = document.getElementById('scanHistoryEmpty');
    if (!tbody) return;
    var stats = appState.statistics || {};
    var lastScan = stats.lastScan || appState.userProfile?.lastScan;
    var scans = [];
    if (stats.totalScanned > 0 || lastScan) {
        scans.push({
            date: lastScan || 'Recently',
            source: stats.source || 'Gmail',
            scanned: stats.totalScanned || 0,
            threats: stats.threatsDetected || stats.threatsBlocked || 0,
            status: 'Completed'
        });
    }
    var mockScans = [
        { date: 'Today', source: 'Gmail', scanned: stats.totalScanned || 0, threats: stats.threatsDetected || 0, status: 'Completed' },
        { date: 'Yesterday', source: 'Gmail', scanned: 45, threats: 2, status: 'Completed' },
        { date: '2 days ago', source: 'Gmail', scanned: 38, threats: 0, status: 'Completed' }
    ];
    if (scans.length === 0 && (stats.totalScanned || 0) === 0) scans = mockScans;
    tbody.innerHTML = scans.map(function(s) {
        return '<tr><td>' + escapeHtml(s.date) + '</td><td>' + escapeHtml(s.source) + '</td><td>' + (s.scanned || 0) + '</td><td>' + (s.threats || 0) + '</td><td><span class="status-badge">' + escapeHtml(s.status) + '</span></td></tr>';
    }).join('');
    if (emptyEl) {
        emptyEl.classList.toggle('hidden', scans.length > 0);
    }
}

async function handleSaveProfile() {
    var newName = (document.getElementById('profileDisplayName').value || '').trim();
    if (newName && newName !== appState.userName) {
        await updateUserName(newName);
    }
    var themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        localStorage.setItem('theme', themeToggle.checked ? 'dark' : 'light');
        applyTheme(themeToggle.checked ? 'dark' : 'light');
    }
    showNotification('Profile saved', 'success');
}

async function loadFlaggedEmails() {
    try {
        const response = await apiCall('/flagged-emails', 'GET');
        if (response && response.success && Array.isArray(response.data)) {
            appState.flaggedEmails = response.data;
            displayFlaggedEmails(response.data);
        } else {
            appState.flaggedEmails = [];
            displayFlaggedEmails([]);
        }
    } catch (error) {
        console.error('Failed to load flagged emails:', error);
        appState.flaggedEmails = [];
        displayFlaggedEmails([]);
    }
}

function displayFlaggedEmails(emails) {
    const container = document.getElementById('flaggedEmailsList');
    
    if (emails.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 40px; color: var(--text-gray);">No flagged emails</p>';
        return;
    }
    
    container.innerHTML = emails.map(email => {
        const safeId = typeof email.id === 'string' ? email.id.replace(/'/g, "\\'") : email.id;
        const onclickView = typeof email.id === 'string' ? `openEmailModal('${safeId}')` : `openEmailModal(${email.id})`;
        const onclickDel = typeof email.id === 'string' ? `deleteEmail('${safeId}')` : `deleteEmail(${email.id})`;
        return `
        <div class="email-item">
            <div class="email-checkbox">
                <input type="checkbox" id="email-${escapeHtml(String(email.id))}">
            </div>
            <div class="email-details">
                <h4>${escapeHtml(email.subject)}</h4>
                <p>${escapeHtml(email.sender)}</p>
                <p class="email-meta">Received: ${escapeHtml(String(email.received_at || email.time || '—'))}${email.flagged_at ? ' · Flagged: ' + escapeHtml(String(email.flagged_at)) : ''}</p>
            </div>
            <div class="threat-badge ${getThreatLevel(email.score)}">${escapeHtml(email.threatType || 'Phishing')}</div>
            <div class="email-score" style="color: ${getScoreColor(email.score)}">${email.score}%</div>
            <div class="email-actions">
                <button class="btn-icon" onclick="${onclickView}" title="View Details">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn-icon" onclick="${onclickDel}" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    }).join('');
}

function getThreatLevel(score) {
    if (score >= 80) return 'high';
    if (score >= 50) return 'medium';
    return 'low';
}

function getScoreColor(score) {
    if (score >= 80) return '#EF4444';
    if (score >= 50) return '#F59E0B';
    return '#10B981';
}

function loadReports() {
    // Simulate API call
    const mockReportData = {
        totalEmails: 1247,
        phishing: 89,
        spam: 143,
        clean: 1015
    };
    
    document.getElementById('reportTotalEmails').textContent = mockReportData.totalEmails.toLocaleString();
    document.getElementById('reportPhishing').textContent = mockReportData.phishing;
    document.getElementById('reportSpam').textContent = mockReportData.spam;
    document.getElementById('reportClean').textContent = mockReportData.clean;
    
    loadActivityTimeline();
}

function loadActivityTimeline() {
    const activities = [
        { time: '2 minutes ago', text: 'Blocked phishing attempt from paypal-verify.tk' },
        { time: '15 minutes ago', text: 'Flagged suspicious email from amazon-security.tk' },
        { time: '1 hour ago', text: 'Completed full inbox scan - 45 emails analyzed' },
        { time: '3 hours ago', text: 'Added newsletter@company.com to whitelist' },
        { time: '5 hours ago', text: 'Updated threat sensitivity to Medium' },
        { time: '1 day ago', text: 'Blocked 12 spam emails' }
    ];
    
    const container = document.getElementById('activityTimeline');
    container.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-time">${activity.time}</div>
            <div class="activity-text">${activity.text}</div>
        </div>
    `).join('');
}

function loadWhitelist() {
    const mockWhitelist = [
        'newsletter@company.com',
        'support@trusted-vendor.com',
        'notifications@github.com',
        'noreply@linkedin.com',
        'team@slack.com'
    ];
    
    const container = document.getElementById('whitelistGrid');
    container.innerHTML = mockWhitelist.map((email, index) => `
        <div class="list-item">
            <span class="list-item-email">${escapeHtml(email)}</span>
            <button class="btn-remove" onclick="removeFromWhitelist('${email}')">
                <i class="fas fa-times"></i> Remove
            </button>
        </div>
    `).join('');
}

function loadBlacklist() {
    const mockBlacklist = [
        'spam@malicious.com',
        'phishing@bad-actor.tk',
        'scam@suspicious-site.net'
    ];
    
    const container = document.getElementById('blacklistGrid');
    container.innerHTML = mockBlacklist.map(email => `
        <div class="list-item">
            <span class="list-item-email">${escapeHtml(email)}</span>
            <button class="btn-remove" onclick="removeFromBlacklist('${email}')">
                <i class="fas fa-times"></i> Remove
            </button>
        </div>
    `).join('');
}

// ============================================
// Action Handlers
// ============================================

async function handleScanNow() {
    showLoading();
    
    try {
        const response = await apiCall('/scan/inbox', 'POST');
        
        if (response && response.success) {
            await loadDashboardData();
            const src = response.data.source === 'gmail' ? 'Gmail' : 'sample inbox';
            let msg = response.data.totalScanned === 0
                ? `Scan complete. No emails in ${src}. ${response.data.source === 'gmail' ? 'Check your inbox or try reconnecting Gmail.' : ''}`
                : `Scan completed! Found ${response.data.threatsFound} threats in ${response.data.totalScanned} emails.`;
            if (response.data.fallbackReason) {
                msg += ' ' + response.data.fallbackReason;
            }
            showNotification(msg, 'success');
        } else {
            const errMsg = (response && response.error) ? response.error : 'Scan failed. Please try again.';
            showNotification(errMsg, 'error');
        }
    } catch (error) {
        console.error('Scan error:', error);
        showNotification('Scan failed. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function handleSaveSettings() {
    const settings = {
        threatThreshold: document.getElementById('threatThreshold').value / 100,
        autoFlag: document.getElementById('autoFlag').checked,
        notifications: document.getElementById('notifications').checked
    };
    
    showLoading();
    
    try {
        const response = await apiCall('/settings', 'PUT', settings);
        
        if (response && response.success) {
            showNotification('Settings saved successfully!', 'success');
        } else {
            showNotification('Failed to save settings', 'error');
        }
    } catch (error) {
        console.error('Settings save error:', error);
        showNotification('Failed to save settings', 'error');
    } finally {
        hideLoading();
    }
}

function handleFilterChange(e) {
    const filterValue = e.target.value;
    console.log('Filter changed to:', filterValue);
    
    // Filter flagged emails based on selection
    let filteredEmails = appState.flaggedEmails;
    
    if (filterValue !== 'all') {
        filteredEmails = appState.flaggedEmails.filter(email => 
            email.threatType.toLowerCase() === filterValue.toLowerCase()
        );
    }
    
    displayFlaggedEmails(filteredEmails);
}

function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    
    const filteredEmails = appState.flaggedEmails.filter(email => 
        email.subject.toLowerCase().includes(searchTerm) ||
        email.sender.toLowerCase().includes(searchTerm)
    );
    
    displayFlaggedEmails(filteredEmails);
}

function applySuspiciousSpansToBody(bodyText, spans, bodyOffset) {
    if (!bodyText || !Array.isArray(spans) || spans.length === 0) return escapeHtml(bodyText);
    var len = bodyText.length;
    var bodySpans = spans
        .filter(function(s) { return s.end > bodyOffset && s.start < bodyOffset + len; })
        .map(function(s) {
            return { start: Math.max(0, s.start - bodyOffset), end: Math.min(len, s.end - bodyOffset), reason: s.reason || 'Suspicious' };
        })
        .sort(function(a, b) { return a.start - b.start; });
    if (bodySpans.length === 0) return escapeHtml(bodyText);
    var out = '';
    var pos = 0;
    for (var i = 0; i < bodySpans.length; i++) {
        var s = bodySpans[i];
        if (s.start > pos) out += escapeHtml(bodyText.slice(pos, s.start));
        out += '<mark class="suspicious-text" title="' + escapeHtml(s.reason) + '">' + escapeHtml(bodyText.slice(s.start, s.end)) + '</mark>';
        pos = s.end;
    }
    if (pos < len) out += escapeHtml(bodyText.slice(pos));
    return out;
}

async function openEmailModal(emailId) {
    let email = appState.flaggedEmails.find(e => e.id == emailId);
    if (!email) {
        var fromRecent = appState.recentThreats.find(function(t) { return t.id == emailId; });
        if (fromRecent) {
            email = {
                id: fromRecent.id,
                subject: fromRecent.subject,
                sender: fromRecent.sender,
                score: fromRecent.score,
                threatType: 'Phishing',
                body: '',
                received_at: fromRecent.time || '',
                flagged_at: ''
            };
        }
    }
    if (!email) {
        try {
            var encId = encodeURIComponent(String(emailId));
            var res = await apiCall('/flagged-emails/' + encId, 'GET');
            if (res && res.success && res.data) {
                var d = res.data;
                email = {
                    id: d.id,
                    subject: d.subject || 'No Subject',
                    sender: d.sender || 'Unknown',
                    score: d.threatScore != null ? d.threatScore : 70,
                    threatType: (d.threatType && d.threatType.charAt(0)) ? d.threatType.charAt(0).toUpperCase() + (d.threatType || '').slice(1) : 'Phishing',
                    body: d.body || '',
                    received_at: d.received_at || '',
                    flagged_at: d.flagged_at || ''
                };
            }
        } catch (err) {
            console.warn('Could not load email details for id:', emailId, err);
        }
    }
    if (!email) return;

    const modal = document.getElementById('emailModal');
    const modalBody = document.getElementById('emailModalBody');
    const safeIdForOnclick = typeof email.id === 'string' ? `'${String(email.id).replace(/'/g, "\\'")}'` : email.id;

    let riskFactors = [
        'Multiple phishing keywords detected',
        'Urgency manipulation detected',
        'Suspicious sender domain',
        'Contains suspicious URLs'
    ];
    let recommendations = [
        'Do not click any links or download attachments',
        'Mark as spam or phishing immediately',
        'Report to your IT security team'
    ];
    let body = email.body || '';
    let threatScore = email.score;
    let threatType = email.threatType || 'Phishing';
    let riskBreakdown = null;
    let suspiciousSpans = [];
    let suspiciousUrls = [];
    let featureContributions = [];

    var receivedAt = email.received_at || '';
    var flaggedAt = email.flagged_at || '';
    try {
        const encId = encodeURIComponent(email.id);
        const response = await apiCall(`/flagged-emails/${encId}`, 'GET');
        if (response && response.success && response.data) {
            const d = response.data;
            threatScore = d.threatScore != null ? d.threatScore : email.score;
            threatType = d.threatType || email.threatType || 'Phishing';
            body = d.body || body;
            if (Array.isArray(d.riskFactors) && d.riskFactors.length) riskFactors = d.riskFactors;
            if (Array.isArray(d.recommendations) && d.recommendations.length) recommendations = d.recommendations;
            if (d.received_at) receivedAt = d.received_at;
            if (d.flagged_at) flaggedAt = d.flagged_at;
            if (d.riskBreakdown) riskBreakdown = d.riskBreakdown;
            if (Array.isArray(d.suspiciousSpans)) suspiciousSpans = d.suspiciousSpans;
            if (Array.isArray(d.suspiciousUrls)) suspiciousUrls = d.suspiciousUrls;
            if (Array.isArray(d.featureContributions)) featureContributions = d.featureContributions;
        }
    } catch (err) {
        console.warn('Could not load full email details:', err);
    }
    if (typeof threatScore === 'number' && threatScore <= 1 && threatScore > 0) threatScore = Math.round(threatScore * 100);

    var bodyOffset = (email.subject || '').length + 2;
    var bodyPreviewHtml = body
        ? '<div style="margin-bottom: 20px;"><h4 style="color: var(--dark-purple); margin-bottom: 10px;">Preview</h4><p style="color: var(--text-dark); white-space: pre-wrap; max-height: 120px; overflow-y: auto;">' +
          applySuspiciousSpansToBody(body, suspiciousSpans, bodyOffset) + '</p></div>'
        : '';

    var riskBreakdownHtml = '';
    if (riskBreakdown && typeof riskBreakdown === 'object') {
        var c = Math.round((riskBreakdown.content || 0) * 100);
        var u = Math.round((riskBreakdown.url || 0) * 100);
        var m = Math.round((riskBreakdown.metadata || 0) * 100);
        riskBreakdownHtml = '<div style="margin-bottom: 20px;"><h4 style="color: var(--dark-purple); margin-bottom: 10px;">Risk breakdown</h4>' +
            '<div style="background: var(--off-white); padding: 12px; border-radius: 10px;">' +
            '<div style="margin-bottom: 8px;"><div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span>Content-based</span><span>' + c + '%</span></div><div style="height: 6px; background: var(--border-color); border-radius: 3px; overflow: hidden;"><div style="height: 100%; width: ' + c + '%; background: var(--danger);"></div></div></div>' +
            '<div style="margin-bottom: 8px;"><div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span>URL-based</span><span>' + u + '%</span></div><div style="height: 6px; background: var(--border-color); border-radius: 3px; overflow: hidden;"><div style="height: 100%; width: ' + u + '%; background: #f59e0b;"></div></div></div>' +
            '<div><div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span>Metadata-based</span><span>' + m + '%</span></div><div style="height: 6px; background: var(--border-color); border-radius: 3px; overflow: hidden;"><div style="height: 100%; width: ' + m + '%; background: #8B5CF6;"></div></div></div>' +
            '</div></div>';
    }

    var suspiciousUrlsHtml = '';
    if (Array.isArray(suspiciousUrls) && suspiciousUrls.length > 0) {
        suspiciousUrlsHtml = '<div style="margin-bottom: 20px;"><h4 style="color: var(--dark-purple); margin-bottom: 10px;">URLs in this email</h4><ul style="list-style: none; padding: 0;">' +
            suspiciousUrls.map(function(item) {
                var url = (item.url || '').substring(0, 80) + (item.url && item.url.length > 80 ? '…' : '');
                var reason = item.reason && item.reason !== 'None' ? '<span class="suspicious-url-badge">' + escapeHtml(item.reason) + '</span>' : '';
                return '<li style="padding: 8px 0; border-bottom: 1px solid var(--border-color); word-break: break-all;">' + escapeHtml(url) + ' ' + reason + '</li>';
            }).join('') + '</ul></div>';
    }

    var featureContributionsHtml = '';
    if (Array.isArray(featureContributions) && featureContributions.length > 0) {
        featureContributionsHtml = '<div style="margin-bottom: 20px;"><h4 style="color: var(--dark-purple); margin-bottom: 10px;"><span onclick="this.parentElement.nextElementSibling.classList.toggle(\'hidden\'); this.classList.toggle(\'open\');" style="cursor: pointer;">Why this score? <i class="fas fa-chevron-down"></i></span></h4>' +
            '<div class="feature-contributions hidden"><ul style="list-style: none; padding: 0; font-size: 0.9rem;">' +
            featureContributions.slice(0, 12).map(function(f) {
                var v = f.contribution != null ? f.contribution : 0;
                var label = (f.feature || f.feature_name || '').replace(/_/g, ' ');
                var cl = v >= 0 ? 'color: var(--danger);' : 'color: var(--text-gray);';
                return '<li style="padding: 4px 0;"><span style="' + cl + '">' + (v >= 0 ? '+' : '') + v.toFixed(3) + '</span> ' + escapeHtml(label) + '</li>';
            }).join('') + '</ul></div></div>';
    }

    modalBody.innerHTML = `
        <div style="margin-bottom: 20px;">
            <h4 style="color: var(--dark-purple); margin-bottom: 10px;">Subject</h4>
            <p style="color: var(--text-dark); font-size: 1.1rem;">${escapeHtml(email.subject)}</p>
        </div>
        <div style="margin-bottom: 20px;">
            <h4 style="color: var(--dark-purple); margin-bottom: 10px;">From</h4>
            <p style="color: var(--text-dark);">${escapeHtml(email.sender)}</p>
        </div>
        <div style="margin-bottom: 20px;">
            <h4 style="color: var(--dark-purple); margin-bottom: 10px;">Date</h4>
            <p style="color: var(--text-dark);">Received: ${escapeHtml(String(receivedAt || '—'))}</p>
            ${flaggedAt ? '<p style="color: var(--text-gray); font-size: 0.9rem;">Flagged on: ' + escapeHtml(String(flaggedAt)) + '</p>' : ''}
        </div>
        ${bodyPreviewHtml}
        <div style="margin-bottom: 20px;">
            <h4 style="color: var(--dark-purple); margin-bottom: 10px;">Threat Analysis <span style="font-size: 0.7rem; background: linear-gradient(135deg, #8B5CF6, #6D28D9); color: #fff; padding: 2px 8px; border-radius: 6px;">NLP + ML</span></h4>
            <div style="background: var(--off-white); padding: 15px; border-radius: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;"><span>Threat Score:</span><strong style="color: ${getScoreColor(threatScore)}">${threatScore}%</strong></div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;"><span>Threat Type:</span><strong>${escapeHtml(threatType)}</strong></div>
                <div style="display: flex; justify-content: space-between;"><span>Risk Level:</span><strong style="color: ${getScoreColor(threatScore)}">${getThreatLevel(threatScore).toUpperCase()}</strong></div>
            </div>
        </div>
        ${riskBreakdownHtml}
        ${suspiciousUrlsHtml}
        ${featureContributionsHtml}
        <div style="margin-bottom: 20px;">
            <h4 style="color: var(--dark-purple); margin-bottom: 10px;">Why was this flagged?</h4>
            <ul style="list-style: none; padding: 0;">${riskFactors.map(r => `<li style="padding: 8px 0; border-bottom: 1px solid var(--border-color);"><i class="fas fa-exclamation-circle" style="color: var(--danger); margin-right: 10px;"></i>${escapeHtml(r)}</li>`).join('')}</ul>
        </div>
        <div style="margin-bottom: 20px;">
            <h4 style="color: var(--dark-purple); margin-bottom: 10px;">Recommendations</h4>
            <div style="background: rgba(239, 68, 68, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid var(--danger);">
                <p style="margin-bottom: 10px;"><strong>⚠️ Do not interact with this email</strong></p>
                <ul style="margin-left: 20px;">${recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('')}</ul>
            </div>
        </div>
        <div style="display: flex; gap: 10px; margin-top: 25px;">
            <button class="btn-primary" onclick="deleteEmail(${safeIdForOnclick}); closeEmailModal();" style="background: var(--danger);"><i class="fas fa-trash"></i> Delete Email</button>
            <button class="btn-primary" onclick="addToBlacklist('${escapeHtml(email.sender).replace(/'/g, "\\'")}'); closeEmailModal();"><i class="fas fa-ban"></i> Block Sender</button>
        </div>
    `;
    modal.classList.add('active');
}

function closeEmailModal() {
    document.getElementById('emailModal').classList.remove('active');
}

function deleteEmail(emailId) {
    appState.flaggedEmails = appState.flaggedEmails.filter(e => e.id != emailId);
    displayFlaggedEmails(appState.flaggedEmails);
    showNotification('Email removed from flagged list', 'success');
}

function removeFromWhitelist(email) {
    console.log('Removing from whitelist:', email);
    showNotification(`Removed ${email} from whitelist`, 'success');
    loadWhitelist();
}

function removeFromBlacklist(email) {
    console.log('Removing from blacklist:', email);
    showNotification(`Removed ${email} from blacklist`, 'success');
    loadBlacklist();
}

function addToBlacklist(email) {
    console.log('Adding to blacklist:', email);
    showNotification(`Added ${email} to blacklist`, 'success');
}

// ============================================
// Authentication Handlers
// ============================================

function handleLogout() {
    console.log('🚪 Logout button clicked');
    
    if (confirm('Are you sure you want to logout?')) {
        console.log('✅ Logout confirmed');
        
        // Clear all auth data
        localStorage.removeItem('authToken');
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userRole');
        localStorage.removeItem('userName');
        localStorage.removeItem('needsNameSetup');
        
        // Stop auto-refresh
        if (typeof stopAutoRefresh === 'function') {
            stopAutoRefresh();
        }
        
        console.log('✅ Redirecting to login page...');
        
        // Redirect to login
        window.location.href = '/login.html';
    } else {
        console.log('❌ Logout cancelled');
    }
}

async function handleConnectGmail() {
    showLoading();
    
    try {
        const response = await apiCall('/auth/google/url', 'GET');
        
        if (response && response.success) {
            if (response.state) sessionStorage.setItem('oauth_state', response.state);
            window.location.href = response.url;
        } else {
            showToast(response.error || 'Failed to connect Gmail', 'error');
        }
    } catch (error) {
        console.error('Gmail connection error:', error);
        showToast('Failed to connect Gmail', 'error');
    } finally {
        hideLoading();
    }
}

function handleChangeName() {
    const currentName = appState.userName;
    const newName = prompt('Enter your new display name:', currentName);
    
    if (newName && newName.trim() !== '' && newName.trim() !== currentName) {
        updateUserName(newName.trim());
    }
}

// ============================================
// Modal Handlers
// ============================================

function openAddWhitelistModal() {
    document.getElementById('addWhitelistModal').classList.add('active');
    document.getElementById('whitelistEmail').value = '';
    document.getElementById('whitelistEmail').focus();
}

function closeAddWhitelistModal() {
    document.getElementById('addWhitelistModal').classList.remove('active');
}

async function submitWhitelist() {
    const email = document.getElementById('whitelistEmail').value.trim();
    
    if (!email) {
        showToast('Please enter an email address', 'warning');
        return;
    }
    
    if (!isValidEmail(email)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }
    
    try {
        const response = await apiCall('/whitelist', 'POST', { email });
        
        if (response && response.success) {
            showToast(`Added ${email} to whitelist`, 'success');
            closeAddWhitelistModal();
            if (appState.currentPage === 'whitelist') {
                loadWhitelist();
            }
        } else {
            showToast(response.error || 'Failed to add to whitelist', 'error');
        }
    } catch (error) {
        console.error('Whitelist error:', error);
        showToast('Failed to add to whitelist', 'error');
    }
}

function openAddBlacklistModal() {
    document.getElementById('addBlacklistModal').classList.add('active');
    document.getElementById('blacklistEmail').value = '';
    document.getElementById('blacklistReason').value = '';
    document.getElementById('blacklistEmail').focus();
}

function closeAddBlacklistModal() {
    document.getElementById('addBlacklistModal').classList.remove('active');
}

async function submitBlacklist() {
    const email = document.getElementById('blacklistEmail').value.trim();
    const reason = document.getElementById('blacklistReason').value.trim();
    
    if (!email) {
        showToast('Please enter an email address', 'warning');
        return;
    }
    
    if (!isValidEmail(email)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }
    
    try {
        const response = await apiCall('/blacklist', 'POST', { email, reason });
        
        if (response && response.success) {
            showToast(`Added ${email} to blacklist`, 'success');
            closeAddBlacklistModal();
            if (appState.currentPage === 'whitelist') {
                loadBlacklist();
            }
        } else {
            showToast(response.error || 'Failed to add to blacklist', 'error');
        }
    } catch (error) {
        console.error('Blacklist error:', error);
        showToast('Failed to add to blacklist', 'error');
    }
}

// ============================================
// Utility Functions
// ============================================

function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

function showNotification(message, type = 'info') {
    showToast(message, type);
    // Badge is updated from loadRecentThreats (real threat count), not from toasts
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-circle' : 
                 type === 'warning' ? 'exclamation-triangle' : 'info-circle';
    
    toast.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function startAutoRefresh() {
    // Refresh dashboard data every 30 seconds
    appState.refreshTimer = setInterval(() => {
        if (appState.currentPage === 'dashboard') {
            loadDashboardData();
        }
    }, CONFIG.refreshInterval);
}

function stopAutoRefresh() {
    if (appState.refreshTimer) {
        clearInterval(appState.refreshTimer);
    }
}

// ============================================
// API Integration Functions (Placeholder)
// ============================================

// These functions would connect to your Python backend
// Replace the mock data with actual API calls

async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        // Add auth token if available
        if (appState.authToken) {
            options.headers['Authorization'] = `Bearer ${appState.authToken}`;
        }
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(CONFIG.apiEndpoint + endpoint, options);
        
        // Handle unauthorized
        if (response.status === 401) {
            localStorage.removeItem('authToken');
            window.location.href = '/login.html';
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        return null;
    }
}

// Example API functions:
// async function fetchDashboardStats() {
//     return await apiCall('/dashboard/stats');
// }
//
// async function scanInbox() {
//     return await apiCall('/scan/inbox', 'POST', { username: CONFIG.username });
// }
//
// async function updateSettings(settings) {
//     return await apiCall('/settings/update', 'POST', settings);
// }

// Make handleLogout globally accessible (for inline onclick)
window.handleLogout = handleLogout;
window.handleChangeName = handleChangeName;
window.openEmailModal = openEmailModal;
window.closeEmailModal = closeEmailModal;
window.deleteEmail = deleteEmail;
window.removeFromWhitelist = removeFromWhitelist;
window.removeFromBlacklist = removeFromBlacklist;
window.addToBlacklist = addToBlacklist;
window.openAddWhitelistModal = openAddWhitelistModal;
window.closeAddWhitelistModal = closeAddWhitelistModal;
window.submitWhitelist = submitWhitelist;
window.openAddBlacklistModal = openAddBlacklistModal;
window.closeAddBlacklistModal = closeAddBlacklistModal;
window.submitBlacklist = submitBlacklist;

console.log('✅ Dashboard application loaded successfully');
console.log('✅ All functions exposed to global scope');
