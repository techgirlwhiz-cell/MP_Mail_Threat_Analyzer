-- ============================================
-- MailThreat Analyzer - Database Setup for PhishDetect
-- Organization: dezrine's Org
-- Copy this ENTIRE file and paste into Supabase SQL Editor
-- Then click RUN
-- ============================================

-- Drop existing tables if they exist (clean slate)
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS gmail_sync_status CASCADE;
DROP TABLE IF EXISTS user_stats CASCADE;
DROP TABLE IF EXISTS organization_stats CASCADE;
DROP TABLE IF EXISTS blacklist CASCADE;
DROP TABLE IF EXISTS whitelist CASCADE;
DROP TABLE IF EXISTS email_scans CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- Drop existing views
DROP VIEW IF EXISTS org_dashboard CASCADE;
DROP VIEW IF EXISTS user_threats_summary CASCADE;

-- Drop existing functions
DROP FUNCTION IF EXISTS update_organization_stats() CASCADE;
DROP FUNCTION IF EXISTS update_user_stats() CASCADE;

-- ============================================
-- 1. Organizations Table
-- ============================================
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    subscription_plan VARCHAR(50) DEFAULT 'basic',
    is_active BOOLEAN DEFAULT true
);

-- ============================================
-- 2. Users Table
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'employee',
    gmail_connected BOOLEAN DEFAULT false,
    gmail_refresh_token TEXT,
    threat_threshold DECIMAL(3,2) DEFAULT 0.60,
    auto_flag BOOLEAN DEFAULT true,
    notifications_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    department VARCHAR(100)
);

-- ============================================
-- 3. Email Scans Table
-- ============================================
CREATE TABLE email_scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    gmail_message_id VARCHAR(255),
    sender_email VARCHAR(255) NOT NULL,
    sender_name VARCHAR(255),
    subject TEXT,
    body_preview TEXT,
    received_at TIMESTAMP WITH TIME ZONE,
    scanned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_threat BOOLEAN NOT NULL,
    threat_score DECIMAL(5,2) NOT NULL,
    threat_type VARCHAR(50),
    confidence_level VARCHAR(20),
    risk_factors JSONB,
    recommendations JSONB,
    is_flagged BOOLEAN DEFAULT false,
    flagged_at TIMESTAMP WITH TIME ZONE,
    action_taken VARCHAR(50),
    false_positive BOOLEAN DEFAULT false
);

-- ============================================
-- 4. Whitelist Table
-- ============================================
CREATE TABLE whitelist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email_address VARCHAR(255) NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by UUID REFERENCES users(id),
    is_org_level BOOLEAN DEFAULT false,
    UNIQUE(user_id, email_address)
);

-- ============================================
-- 5. Blacklist Table
-- ============================================
CREATE TABLE blacklist (
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
-- 6. Organization Statistics Table
-- ============================================
CREATE TABLE organization_stats (
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
-- 7. User Statistics Table
-- ============================================
CREATE TABLE user_stats (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_emails_scanned INTEGER DEFAULT 0,
    total_threats_detected INTEGER DEFAULT 0,
    threats_blocked INTEGER DEFAULT 0,
    false_positives_reported INTEGER DEFAULT 0,
    last_scan TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 8. Audit Log Table
-- ============================================
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 9. Gmail Sync Status Table
-- ============================================
CREATE TABLE gmail_sync_status (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    last_history_id VARCHAR(255),
    sync_status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    emails_synced_count INTEGER DEFAULT 0
);

-- ============================================
-- Create Indexes
-- ============================================
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_scans_user ON email_scans(user_id);
CREATE INDEX idx_scans_org ON email_scans(organization_id);
CREATE INDEX idx_scans_threat ON email_scans(is_threat, scanned_at DESC);
CREATE INDEX idx_scans_time ON email_scans(scanned_at DESC);
CREATE INDEX idx_audit_org ON audit_log(organization_id, created_at DESC);
CREATE INDEX idx_audit_user ON audit_log(user_id, created_at DESC);

-- ============================================
-- Functions for Auto-Updates
-- ============================================

-- Update organization stats function
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

-- Update user stats function
CREATE OR REPLACE FUNCTION update_user_stats()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_stats (user_id, total_emails_scanned, total_threats_detected, threats_blocked, last_scan, last_updated)
    VALUES (
        NEW.user_id,
        1,
        CASE WHEN NEW.is_threat THEN 1 ELSE 0 END,
        CASE WHEN NEW.is_threat AND NEW.is_flagged THEN 1 ELSE 0 END,
        NEW.scanned_at,
        NOW()
    )
    ON CONFLICT (user_id) DO UPDATE
    SET 
        total_emails_scanned = user_stats.total_emails_scanned + 1,
        total_threats_detected = user_stats.total_threats_detected + CASE WHEN NEW.is_threat THEN 1 ELSE 0 END,
        threats_blocked = user_stats.threats_blocked + CASE WHEN NEW.is_threat AND NEW.is_flagged THEN 1 ELSE 0 END,
        last_scan = NEW.scanned_at,
        last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Create Triggers
-- ============================================
CREATE TRIGGER trigger_update_org_stats
AFTER INSERT ON email_scans
FOR EACH ROW
EXECUTE FUNCTION update_organization_stats();

CREATE TRIGGER trigger_update_user_stats
AFTER INSERT ON email_scans
FOR EACH ROW
EXECUTE FUNCTION update_user_stats();

-- ============================================
-- Create Views
-- ============================================

-- Organization dashboard view
CREATE OR REPLACE VIEW org_dashboard AS
SELECT 
    o.id as organization_id,
    o.name as organization_name,
    o.domain,
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
    ) as threat_rate_percentage,
    os.last_updated
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
    u.organization_id,
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
-- Insert YOUR Organization: dezrine's Org
-- ============================================

-- IMPORTANT: Replace 'your-gmail@gmail.com' with YOUR actual Gmail address below!

INSERT INTO organizations (name, domain, subscription_plan) 
VALUES ('dezrine''s Org', 'dezrine.com', 'enterprise');

-- Get the organization ID and create your CEO account
DO $$
DECLARE
    org_id UUID;
    ceo_id UUID;
BEGIN
    -- Get organization ID
    SELECT id INTO org_id FROM organizations WHERE name = 'dezrine''s Org';
    
    -- Insert CEO user (YOU!)
    -- ⚠️ REPLACE 'your-gmail@gmail.com' with YOUR actual Gmail address
    INSERT INTO users (organization_id, email, full_name, role, is_active)
    VALUES (org_id, 'your-gmail@gmail.com', 'Dezrine Admin', 'ceo', true)
    RETURNING id INTO ceo_id;
    
    -- Initialize organization stats
    INSERT INTO organization_stats (organization_id, total_users)
    VALUES (org_id, 1);
    
    -- Initialize CEO user stats
    INSERT INTO user_stats (user_id)
    VALUES (ceo_id);
    
    RAISE NOTICE '✅ Your organization "dezrine''s Org" has been created!';
    RAISE NOTICE '📧 CEO account created with email: your-gmail@gmail.com';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  IMPORTANT: Update the CEO email above with your actual Gmail!';
    
END $$;

-- ============================================
-- Success Message
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ DATABASE SETUP COMPLETE FOR PHISHDETECT!';
    RAISE NOTICE '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━';
    RAISE NOTICE '';
    RAISE NOTICE '📋 Tables Created (9 total):';
    RAISE NOTICE '   ✓ organizations';
    RAISE NOTICE '   ✓ users';
    RAISE NOTICE '   ✓ email_scans';
    RAISE NOTICE '   ✓ whitelist';
    RAISE NOTICE '   ✓ blacklist';
    RAISE NOTICE '   ✓ organization_stats';
    RAISE NOTICE '   ✓ user_stats';
    RAISE NOTICE '   ✓ audit_log';
    RAISE NOTICE '   ✓ gmail_sync_status';
    RAISE NOTICE '';
    RAISE NOTICE '🏢 Your Organization:';
    RAISE NOTICE '   Name: dezrine''s Org';
    RAISE NOTICE '   Domain: dezrine.com';
    RAISE NOTICE '   Plan: Enterprise';
    RAISE NOTICE '';
    RAISE NOTICE '👤 Your CEO Account:';
    RAISE NOTICE '   Email: your-gmail@gmail.com (⚠️ UPDATE THIS!)';
    RAISE NOTICE '   Role: CEO';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Next Steps:';
    RAISE NOTICE '   1. Update the CEO email in the SQL above';
    RAISE NOTICE '   2. Set up Gmail API (see GMAIL_SETUP_GUIDE.md)';
    RAISE NOTICE '   3. Start dashboard: ./start_dashboard.sh';
    RAISE NOTICE '   4. Open: http://localhost:5001';
    RAISE NOTICE '';
    RAISE NOTICE '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━';
    RAISE NOTICE '';
END $$;

-- Show final summary
SELECT 
    'Organizations' as table_name, 
    COUNT(*) as record_count,
    string_agg(name, ', ') as names
FROM organizations
UNION ALL
SELECT 
    'Users', 
    COUNT(*), 
    string_agg(email, ', ')
FROM users
UNION ALL
SELECT 
    'Organization Stats', 
    COUNT(*),
    NULL
FROM organization_stats
UNION ALL
SELECT 
    'User Stats', 
    COUNT(*),
    NULL
FROM user_stats;

-- Display organization details
SELECT 
    'Organization' as info_type,
    name as value
FROM organizations
UNION ALL
SELECT 
    'Domain',
    domain
FROM organizations
UNION ALL
SELECT 
    'Plan',
    subscription_plan
FROM organizations;
