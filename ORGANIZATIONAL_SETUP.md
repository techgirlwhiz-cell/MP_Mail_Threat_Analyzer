# 🏢 Organizational Setup Guide - MailThreat Analyzer

## Complete Guide for CEOs and Managers

---

## 🎯 Overview

**MailThreat Analyzer** is now configured for organizational use with:

✅ **Role-Based Access Control**
- CEO: Full organizational control
- Manager: Department/team monitoring
- Employee: Personal email monitoring

✅ **Centralized Management**
- Managers create employee accounts
- Monitor threat statistics across organization
- Privacy-compliant (no email content access)

✅ **Real Gmail Integration**
- Connects to actual Gmail accounts
- Real-time threat detection
- Automatic flagging in Gmail

✅ **Supabase Database**
- Secure cloud storage
- Real-time updates
- Scalable for any organization size

---

## 📋 What You Need

### 1. Database (Supabase - Already Configured!)

Your Supabase instance is ready:
- **URL**: `https://bdhleygddjoxoeuqsirk.supabase.co`
- **Status**: ✅ Connected and ready

### 2. Gmail API Credentials

Follow `GMAIL_SETUP_GUIDE.md` to:
- Set up Google Cloud project
- Enable Gmail API
- Create OAuth credentials
- Configure for organization

### 3. Admin Access

You'll need:
- CEO/Admin email for first login
- Google Workspace (optional, for domain-wide)
- Employee email list

---

## 🚀 Quick Setup (5 Steps)

### Step 1: Set Up Database

1. **Run Database Schema**
   - Open Supabase dashboard: https://supabase.com/dashboard
   - Go to your project → SQL Editor
   - Copy entire content from `database_schema.sql`
   - Click "Run"
   - Wait for completion (creates all tables)

2. **Verify Tables Created**
   - Go to "Table Editor"
   - You should see:
     - organizations
     - users
     - email_scans
     - whitelist
     - blacklist
     - organization_stats
     - user_stats
     - audit_log
     - gmail_sync_status

### Step 2: Create Your Organization

Run this in Supabase SQL Editor (replace with your info):

```sql
-- Create your organization
INSERT INTO organizations (name, domain, subscription_plan) 
VALUES ('Your Company Name', 'yourcompany.com', 'enterprise')
RETURNING id;

-- Note the organization ID from the result
```

### Step 3: Create CEO/Admin Account

```sql
-- Replace YOUR_ORG_ID with the ID from Step 2
INSERT INTO users (
    organization_id,
    email,
    full_name,
    role
) VALUES (
    'YOUR_ORG_ID',  -- Your organization ID
    'ceo@yourcompany.com',  -- CEO email
    'John CEO',  -- CEO name
    'ceo'  -- Role
);

-- Initialize stats
INSERT INTO user_stats (user_id)
SELECT id FROM users WHERE email = 'ceo@yourcompany.com';

INSERT INTO organization_stats (organization_id)
VALUES ('YOUR_ORG_ID');
```

### Step 4: Install Gmail Dependencies

```bash
source venv/bin/activate
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client supabase
```

### Step 5: Start the System

```bash
./start_dashboard.sh
```

Go to: http://localhost:5001

---

## 👔 For CEOs/Administrators

### Your Dashboard Features:

1. **Organization Overview**
   - Total employees monitored
   - Threats detected (24h, 7d, 30d)
   - Organization-wide threat rate
   - Top threat types

2. **Employee Management**
   - Create new employee accounts
   - Assign to departments
   - Set individual threat thresholds
   - Activate/deactivate accounts

3. **Threat Monitoring**
   - See which employees receive most threats
   - Identify threat patterns
   - Export reports
   - View trends over time

4. **Privacy Controls**
   - You see only statistics, not email content
   - Employees notified of monitoring
   - Compliance-friendly approach

### Creating Employee Accounts:

**Option 1: Through Dashboard**
1. Login as CEO/Admin
2. Go to "Employee Management"
3. Click "Add Employee"
4. Enter:
   - Full name
   - Email address
   - Department
   - Role (employee/manager)
   - Threat threshold (default 0.60)
5. Click "Create Account"
6. Employee receives invitation email

**Option 2: Bulk Import (SQL)**

```sql
-- Import multiple employees at once
INSERT INTO users (organization_id, email, full_name, role, department) VALUES
('YOUR_ORG_ID', 'employee1@company.com', 'John Doe', 'employee', 'Sales'),
('YOUR_ORG_ID', 'employee2@company.com', 'Jane Smith', 'employee', 'Marketing'),
('YOUR_ORG_ID', 'manager1@company.com', 'Bob Manager', 'manager', 'Sales');

-- Initialize stats for all
INSERT INTO user_stats (user_id)
SELECT id FROM users 
WHERE organization_id = 'YOUR_ORG_ID' 
AND id NOT IN (SELECT user_id FROM user_stats);
```

---

## 📊 For Managers

### Your Dashboard Features:

1. **Team Overview**
   - Monitor your department's threat statistics
   - See high-risk team members
   - Review flagged emails count

2. **Team Member Details**
   - Individual threat statistics
   - Recent threat activity
   - Compliance status

3. **Reporting**
   - Generate department reports
   - Export threat data
   - Trend analysis

4. **Limited Access**
   - Can only see your department
   - Cannot access other departments
   - Privacy-compliant monitoring

### Creating Team Member Accounts:

Same as CEO, but limited to your department.

---

## 👨‍💼 For Employees

### Your Dashboard Features:

1. **Personal Threats**
   - See your flagged emails
   - Review threat analysis
   - Take action (delete, whitelist sender)

2. **Protection Status**
   - Your threat detection settings
   - Emails scanned count
   - Threats blocked

3. **Gmail Integration**
   - Connect your work Gmail
   - Auto-scan new emails
   - See flags in Gmail directly

4. **Settings**
   - Adjust threat sensitivity
   - Manage whitelist/blacklist
   - View your statistics

### First Time Setup (Employees):

1. **Receive Invitation**
   - Manager creates your account
   - You receive email invitation

2. **Login**
   - Go to: http://your-company-url:5001
   - Login with your work email
   - Set up 2FA (if enabled)

3. **Connect Gmail**
   - Click "Connect Gmail"
   - Authorize MailThreat Analyzer
   - Grant permissions

4. **Initial Scan**
   - System scans your recent emails
   - Threats are flagged
   - You see results in dashboard

---

## 🔒 Privacy & Compliance

### What Managers/CEO Can See:

✅ **Statistics Only:**
- Number of threats detected
- Threat types breakdown
- Time patterns
- Sender domains (aggregated)

❌ **Cannot See:**
- Email subject lines
- Email body content
- Individual email details
- Who sent what to whom

### What's Stored:

**In Database:**
- Email metadata (sender, timestamp)
- Threat analysis results
- Risk factors (generic)
- Action taken

**NOT Stored:**
- Full email body content
- Attachments
- Personal conversations

### Compliance:

✅ **GDPR Compliant**
- Users notified of monitoring
- Minimal data collection
- Right to access/delete

✅ **SOC 2 Ready**
- Audit logs
- Access controls
- Encryption

---

## 🔧 Configuration Options

### Organization Settings:

Edit in Supabase `organizations` table:

```sql
UPDATE organizations
SET 
    subscription_plan = 'enterprise',  -- basic, premium, enterprise
    is_active = true
WHERE domain = 'yourcompany.com';
```

### User Settings:

```sql
-- Update individual user
UPDATE users
SET 
    threat_threshold = 0.70,  -- 0.00 to 1.00 (higher = less sensitive)
    auto_flag = true,         -- Auto-flag threats
    notifications_enabled = true,
    department = 'Engineering'
WHERE email = 'user@company.com';
```

### Organizational Whitelist:

```sql
-- Add org-wide trusted sender
INSERT INTO whitelist (
    organization_id,
    email_address,
    is_org_level,
    added_by
) VALUES (
    'YOUR_ORG_ID',
    'trusted@partner.com',
    true,  -- Org-level (applies to all users)
    'CEO_USER_ID'
);
```

---

## 📈 Monitoring & Reports

### Real-Time Dashboard:

**Organization View (CEO):**
```
┌─────────────────────────────────────────┐
│  MailThreat Analyzer - Organization     │
├─────────────────────────────────────────┤
│  Total Employees: 156                   │
│  Threats Today: 23                      │
│  Threats This Week: 187                 │
│  Threat Rate: 4.2%                      │
├─────────────────────────────────────────┤
│  High-Risk Employees:                   │
│  • John Doe (Sales) - 12 threats        │
│  • Jane Smith (Marketing) - 8 threats   │
│  • Bob Wilson (IT) - 7 threats          │
├─────────────────────────────────────────┤
│  Top Threat Types:                      │
│  • Phishing: 62%                        │
│  • Spam: 28%                            │
│  • Malware: 10%                         │
└─────────────────────────────────────────┘
```

**Department View (Manager):**
```
┌─────────────────────────────────────────┐
│  Sales Department - Threat Monitor      │
├─────────────────────────────────────────┤
│  Team Members: 23                       │
│  Threats Today: 8                       │
│  Avg Threat Score: 0.65                 │
├─────────────────────────────────────────┤
│  Team Members:                          │
│  ✓ John Doe - 2 threats                 │
│  ✓ Mary Johnson - 1 threat              │
│  ✓ Steve Brown - 5 threats ⚠️          │
│  ✓ Lisa Davis - 0 threats               │
└─────────────────────────────────────────┘
```

### Export Reports:

1. **CEO Dashboard** → "Reports" → "Export"
2. Choose format: CSV, PDF, Excel
3. Select date range
4. Download report

---

## 🆘 Troubleshooting

### Issue: Employees Can't Connect Gmail

**Solution:**
1. Verify Gmail API is enabled
2. Check OAuth credentials are correct
3. Ensure employee email is added as test user
4. Try from incognito/private browser

### Issue: Manager Can't See Department

**Solution:**
```sql
-- Verify manager's department assignment
SELECT * FROM users WHERE email = 'manager@company.com';

-- Update if needed
UPDATE users SET department = 'Sales' WHERE email = 'manager@company.com';
```

### Issue: Statistics Not Updating

**Solution:**
```sql
-- Manually refresh stats
SELECT update_organization_stats();
```

### Issue: No Threats Detected

**Check:**
1. Gmail is connected (check `gmail_sync_status` table)
2. Recent scan completed
3. Threat threshold not too high
4. Test with known phishing email

---

## 📞 Support

### For Administrators:

- Database issues: Check Supabase dashboard
- Gmail API: Review Google Cloud Console
- Configuration: Edit `web_backend.py`

### For Users:

- Login issues: Contact your manager/admin
- Gmail connection: See `GMAIL_SETUP_GUIDE.md`
- Settings: Use in-app settings page

---

## ✅ Launch Checklist

- [ ] Supabase database schema deployed
- [ ] Organization created in database
- [ ] CEO/Admin account created
- [ ] Gmail API configured
- [ ] OAuth credentials set up
- [ ] Dependencies installed
- [ ] Server started successfully
- [ ] CEO can login
- [ ] Test employee account created
- [ ] Test Gmail connection works
- [ ] Test threat detection works
- [ ] Manager dashboard accessible
- [ ] Reports can be generated

---

## 🎉 You're Ready!

**Your MailThreat Analyzer organizational system is configured!**

**Next Steps:**
1. ✅ Create employee accounts
2. ✅ Have employees connect Gmail
3. ✅ Monitor threats from manager dashboard
4. ✅ Review weekly reports

**Dashboard URL:** http://localhost:5001 (or your production URL)

---

**Need help?** Check `GMAIL_SETUP_GUIDE.md` and `TROUBLESHOOTING.md`
