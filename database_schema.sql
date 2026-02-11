-- MailThreat Analyzer - Supabase Database Schema
-- Run this in your Supabase SQL Editor

-- ============================================
-- 1. Organizations Table
-- ============================================
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL, -- e.g., company.com
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    subscription_plan VARCHAR(50) DEFAULT 'basic', -- basic, premium, enterprise
    is_active BOOLEAN DEFAULT true
);

-- ============================================
-- 2. Users Table (with roles)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'employee', -- ceo, manager, employee
    gmail_connected BOOLEAN DEFAULT false,
    gmail_refresh_token TEXT, -- Encrypted Gmail OAuth token
    threat_threshold DECIMAL(3,2) DEFAULT 0.60, -- 0.00 to 1.00
    auto_flag BOOLEAN DEFAULT true,
    notifications_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id), -- Manager/CEO who created this user
    department VARCHAR(100)
);

-- ============================================
-- 3. Email Scans Table
-- ============================================
CREATE TABLE IF NOT EXISTS email_scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    gmail_message_id VARCHAR(255), -- Gmail message ID
    sender_email VARCHAR(255) NOT NULL,
    sender_name VARCHAR(255),
    subject TEXT,
    body_preview TEXT, -- First 500 chars
    received_at TIMESTAMP WITH TIME ZONE,
    scanned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_threat BOOLEAN NOT NULL,
    threat_score DECIMAL(5,2) NOT NULL, -- 0.00 to 100.00
    threat_type VARCHAR(50), -- phishing, spam, malware, suspicious
    confidence_level VARCHAR(20), -- high, medium, low
    risk_factors JSONB, -- Array of risk factors
    recommendations JSONB, -- Array of recommendations
    is_flagged BOOLEAN DEFAULT false,
    flagged_at TIMESTAMP WITH TIME ZONE,
    action_taken VARCHAR(50), -- none, deleted, moved_to_spam, whitelisted
    false_positive BOOLEAN DEFAULT false, -- User reported false positive
    INDEX idx_user_scans (user_id, scanned_at DESC),
    INDEX idx_org_scans (organization_id, scanned_at DESC),
    INDEX idx_threats (is_threat, scanned_at DESC)
);

-- ============================================
-- 4. Whitelist Table
-- ============================================
CREATE TABLE IF NOT EXISTS whitelist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email_address VARCHAR(255) NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by UUID REFERENCES users(id),
    is_org_level BOOLEAN DEFAULT false, -- True if org-wide, false if user-specific
    UNIQUE(user_id, email_address)
);

-- ============================================
-- 5. Blacklist Table
-- ============================================
CREATE TABLE IF NOT EXISTS blacklist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email_address VARCHAR(255) NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by UUID REFERENCES users(id),
    is_org_level BOOLEAN DEFAULT false,
    reason TEXT,
    UNIQUE(user_id, email_address)
);

-- ============================================
-- 6. Organization Statistics (Cached)
-- ============================================
CREATE TABLE IF NOT EXISTS organization_stats (
    organization_id UUID PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
    total_users INTEGER DEFAULT 0,
    total_emails_scanned INTEGER DEFAULT 0,
    total_threats_detected INTEGER DEFAULT 0,
    threats_last_24h INTEGER DEFAULT 0,
    threats_last_7d INTEGER DEFAULT 0,
    threats_last_30d INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 7. User Statistics (Cached)
-- ============================================
CREATE TABLE IF NOT EXISTS user_stats (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_emails_scanned INTEGER DEFAULT 0,
    total_threats_detected INTEGER DEFAULT 0,
    threats_blocked INTEGER DEFAULT 0,
    false_positives_reported INTEGER DEFAULT 0,
    last_scan TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 8. Audit Log
-- ============================================
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- user_created, scan_completed, settings_changed, etc.
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_audit_org (organization_id, created_at DESC),
    INDEX idx_audit_user (user_id, created_at DESC)
);

-- ============================================
-- 9. Gmail Sync Status
-- ============================================
CREATE TABLE IF NOT EXISTS gmail_sync_status (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    last_history_id VARCHAR(255), -- Gmail history ID for incremental sync
    sync_status VARCHAR(50) DEFAULT 'pending', -- pending, syncing, completed, error
    error_message TEXT,
    emails_synced_count INTEGER DEFAULT 0
);

-- ============================================
-- Row Level Security (RLS) Policies
-- ============================================

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE whitelist ENABLE ROW LEVEL SECURITY;
ALTER TABLE blacklist ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;

-- Users can see their own data
CREATE POLICY users_own_data ON users
    FOR ALL USING (auth.uid()::text = id::text);

-- Managers can see users in their organization
CREATE POLICY managers_see_org_users ON users
    FOR SELECT USING (
        organization_id IN (
            SELECT organization_id FROM users 
            WHERE id::text = auth.uid()::text 
            AND role IN ('manager', 'ceo')
        )
    );

-- Users can see their own email scans
CREATE POLICY users_own_scans ON email_scans
    FOR ALL USING (user_id::text = auth.uid()::text);

-- Managers can see all scans in their organization
CREATE POLICY managers_see_org_scans ON email_scans
    FOR SELECT USING (
        organization_id IN (
            SELECT organization_id FROM users 
            WHERE id::text = auth.uid()::text 
            AND role IN ('manager', 'ceo')
        )
    );

-- ============================================
-- Indexes for Performance
-- ============================================

CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_scans_user ON email_scans(user_id);
CREATE INDEX idx_scans_org ON email_scans(organization_id);
CREATE INDEX idx_scans_threat ON email_scans(is_threat, scanned_at DESC);
CREATE INDEX idx_scans_time ON email_scans(scanned_at DESC);

-- ============================================
-- Functions and Triggers
-- ============================================

-- Update organization stats
CREATE OR REPLACE FUNCTION update_organization_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE organization_stats
    SET 
        total_emails_scanned = (
            SELECT COUNT(*) FROM email_scans 
            WHERE organization_id = NEW.organization_id
        ),
        total_threats_detected = (
            SELECT COUNT(*) FROM email_scans 
            WHERE organization_id = NEW.organization_id AND is_threat = true
        ),
        threats_last_24h = (
            SELECT COUNT(*) FROM email_scans 
            WHERE organization_id = NEW.organization_id 
            AND is_threat = true 
            AND scanned_at > NOW() - INTERVAL '24 hours'
        ),
        threats_last_7d = (
            SELECT COUNT(*) FROM email_scans 
            WHERE organization_id = NEW.organization_id 
            AND is_threat = true 
            AND scanned_at > NOW() - INTERVAL '7 days'
        ),
        threats_last_30d = (
            SELECT COUNT(*) FROM email_scans 
            WHERE organization_id = NEW.organization_id 
            AND is_threat = true 
            AND scanned_at > NOW() - INTERVAL '30 days'
        ),
        last_updated = NOW()
    WHERE organization_id = NEW.organization_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_org_stats
AFTER INSERT ON email_scans
FOR EACH ROW
EXECUTE FUNCTION update_organization_stats();

-- Update user stats
CREATE OR REPLACE FUNCTION update_user_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_stats
    SET 
        total_emails_scanned = (
            SELECT COUNT(*) FROM email_scans WHERE user_id = NEW.user_id
        ),
        total_threats_detected = (
            SELECT COUNT(*) FROM email_scans 
            WHERE user_id = NEW.user_id AND is_threat = true
        ),
        threats_blocked = (
            SELECT COUNT(*) FROM email_scans 
            WHERE user_id = NEW.user_id AND is_threat = true AND is_flagged = true
        ),
        last_scan = NEW.scanned_at,
        last_updated = NOW()
    WHERE user_id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_stats
AFTER INSERT ON email_scans
FOR EACH ROW
EXECUTE FUNCTION update_user_stats();

-- ============================================
-- Sample Data (Optional - for testing)
-- ============================================

-- Insert sample organization
INSERT INTO organizations (name, domain) 
VALUES ('Demo Company', 'democompany.com')
ON CONFLICT (domain) DO NOTHING;

-- Insert sample CEO
INSERT INTO users (organization_id, email, full_name, role)
SELECT id, 'ceo@democompany.com', 'John CEO', 'ceo'
FROM organizations WHERE domain = 'democompany.com'
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- Views for Easy Querying
-- ============================================

-- Organization dashboard view
CREATE OR REPLACE VIEW org_dashboard AS
SELECT 
    o.id as organization_id,
    o.name as organization_name,
    os.total_users,
    os.total_emails_scanned,
    os.total_threats_detected,
    os.threats_last_24h,
    os.threats_last_7d,
    os.threats_last_30d,
    ROUND(
        CASE 
            WHEN os.total_emails_scanned > 0 
            THEN (os.total_threats_detected::DECIMAL / os.total_emails_scanned * 100)
            ELSE 0 
        END, 2
    ) as threat_rate_percentage
FROM organizations o
LEFT JOIN organization_stats os ON o.id = os.organization_id;

-- User threats summary view
CREATE OR REPLACE VIEW user_threats_summary AS
SELECT 
    u.id as user_id,
    u.email,
    u.full_name,
    u.role,
    u.department,
    us.total_emails_scanned,
    us.total_threats_detected,
    us.threats_blocked,
    us.last_scan,
    ROUND(
        CASE 
            WHEN us.total_emails_scanned > 0 
            THEN (us.total_threats_detected::DECIMAL / us.total_emails_scanned * 100)
            ELSE 0 
        END, 2
    ) as threat_rate_percentage
FROM users u
LEFT JOIN user_stats us ON u.id = us.user_id;

-- ============================================
-- NOTES:
-- ============================================
-- 1. Run this entire script in your Supabase SQL Editor
-- 2. Make sure to enable RLS in your Supabase project settings
-- 3. Update the auth.uid() references if using custom auth
-- 4. Adjust indexes based on your query patterns
-- 5. Monitor performance and add indexes as needed
