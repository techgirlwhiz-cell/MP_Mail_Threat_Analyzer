# ✅ MailThreat Analyzer - Testing Checklist

Use this checklist to verify everything is working correctly!

---

## 🚀 Pre-Testing Setup

- [ ] Navigate to project directory: `cd "/Users/desrine/Documents/Major Project_V1"`
- [ ] Start the server: `./start_app.sh` or `python3 web_backend.py`
- [ ] Server shows "Server ready!" message
- [ ] Open browser to http://localhost:5001/login.html

---

## 🔐 Login & Authentication Tests

### Login Page
- [ ] Login page loads with purple gradient design
- [ ] Logo displays "MailThreat Analyzer"
- [ ] Both input fields are visible (email and password)
- [ ] "Remember me" checkbox is visible
- [ ] "Sign In" button is visible
- [ ] "Sign in with Google" button is visible

### Successful Login
- [ ] Enter: `demo@example.com` and `demo123`
- [ ] Click "Sign In"
- [ ] Loading spinner appears
- [ ] Redirected to dashboard (index.html)
- [ ] User name shows in sidebar ("Demo User")
- [ ] User email shows in sidebar ("demo@example.com")

### Failed Login
- [ ] Go back to login page: http://localhost:5001/login.html
- [ ] Enter wrong credentials
- [ ] Click "Sign In"
- [ ] Error message appears in red box
- [ ] NOT redirected to dashboard
- [ ] Can try again

### Auto-Login (Session Persistence)
- [ ] After successful login, close browser
- [ ] Reopen browser to http://localhost:5001
- [ ] Automatically redirected to dashboard (if "remember me" was checked)
- [ ] OR taken to login page (if "remember me" was not checked)

---

## 🏠 Dashboard Tests

### Page Load
- [ ] Dashboard page loads with statistics
- [ ] Header shows "Dashboard"
- [ ] "Scan Now" button visible in header
- [ ] Notification bell visible
- [ ] Four stat cards visible (Total Scanned, Threats Detected, etc.)
- [ ] Protection status circle shows percentage
- [ ] Recent threats list displays

### Navigation Sidebar
- [ ] Dashboard link highlighted (active)
- [ ] Click "Flagged Emails" → navigates to flagged page
- [ ] Click "Reports" → navigates to reports page
- [ ] Click "Whitelist" → navigates to whitelist page
- [ ] Click "Settings" → navigates to settings page
- [ ] Click "Dashboard" → returns to dashboard
- [ ] Active page is highlighted in purple

### Scan Now Button
- [ ] Click "Scan Now" button
- [ ] Loading overlay appears with spinner
- [ ] Text shows "Scanning emails..."
- [ ] After ~2 seconds, overlay disappears
- [ ] Toast notification appears (green)
- [ ] Says "Scan completed! Found X new threats"
- [ ] Statistics update on dashboard

---

## 📧 Flagged Emails Tests

### Page Display
- [ ] Navigate to "Flagged Emails"
- [ ] Page title changes to "Flagged Emails"
- [ ] Filter dropdown visible (All Threats, Phishing, Spam, Malware)
- [ ] Search box visible
- [ ] List of flagged emails displays
- [ ] Each email shows: subject, sender, threat type, score, actions

### Filtering
- [ ] Select "Phishing" from filter dropdown
- [ ] Only phishing emails shown
- [ ] Select "All Threats"
- [ ] All emails shown again

### Search
- [ ] Type "paypal" in search box
- [ ] Only emails matching "paypal" shown
- [ ] Clear search box
- [ ] All emails shown again

### View Email Details
- [ ] Click eye icon on any email
- [ ] Modal opens showing email details
- [ ] Subject displayed
- [ ] Sender displayed
- [ ] Threat score displayed
- [ ] Risk factors listed
- [ ] Recommendations shown
- [ ] "Delete Email" button visible
- [ ] "Block Sender" button visible
- [ ] Click X to close modal
- [ ] Modal closes

### Delete Email
- [ ] Click trash icon on any email
- [ ] Email removed from list
- [ ] Toast notification appears
- [ ] Says "Email deleted successfully"

---

## 📊 Reports Tests

### Reports Page
- [ ] Navigate to "Reports"
- [ ] Page title changes to "Reports"
- [ ] "Export" button visible
- [ ] Threat Analysis Report card visible
- [ ] Shows: Total Emails, Phishing, Spam, Clean
- [ ] Numbers are displayed (not 0)
- [ ] Weekly Activity card visible
- [ ] Activity timeline shows recent events

---

## ✅ Whitelist & Blacklist Tests

### Whitelist - Add Entry
- [ ] Navigate to "Whitelist & Blacklist"
- [ ] Whitelist section visible
- [ ] Click "+ Add Sender" button (under Whitelist)
- [ ] Modal opens with title "Add Trusted Sender"
- [ ] Input field for email address visible
- [ ] Enter: `trusted@example.com`
- [ ] Click "Add to Whitelist"
- [ ] Modal closes
- [ ] Toast notification appears (green)
- [ ] Says "Added trusted@example.com to whitelist"
- [ ] Whitelist updates with new entry

### Whitelist - Invalid Email
- [ ] Click "+ Add Sender" again
- [ ] Enter invalid email: `notanemail`
- [ ] Click "Add to Whitelist"
- [ ] Toast notification appears (red/orange)
- [ ] Says "Please enter a valid email address"
- [ ] Modal stays open

### Whitelist - Remove Entry
- [ ] Find any email in whitelist
- [ ] Click "Remove" button
- [ ] Toast notification appears
- [ ] Says "Removed [email] from whitelist"
- [ ] Email removed from list

### Blacklist - Add Entry
- [ ] Click "+ Add Sender" button (under Blacklist)
- [ ] Modal opens with title "Block Sender"
- [ ] Input field for email address visible
- [ ] Textarea for reason visible
- [ ] Enter: `spam@malicious.com`
- [ ] Enter reason: `Suspicious phishing attempt`
- [ ] Click "Add to Blacklist"
- [ ] Modal closes
- [ ] Toast notification appears (green)
- [ ] Says "Added spam@malicious.com to blacklist"
- [ ] Blacklist updates with new entry

### Blacklist - Remove Entry
- [ ] Find any email in blacklist
- [ ] Click "Remove" button
- [ ] Toast notification appears
- [ ] Says "Removed [email] from blacklist"
- [ ] Email removed from list

---

## ⚙️ Settings Tests

### Settings Page
- [ ] Navigate to "Settings"
- [ ] Page title changes to "Settings"
- [ ] "Detection Settings" card visible
- [ ] "Account Information" card visible

### Detection Settings
- [ ] Threat Sensitivity slider visible
- [ ] Current value displayed (e.g., "60%")
- [ ] Move slider left
- [ ] Value updates in real-time
- [ ] Move slider right
- [ ] Value updates
- [ ] Auto-Flag toggle switch visible
- [ ] Click toggle switch
- [ ] Switch changes state (on/off)
- [ ] Email Notifications toggle visible
- [ ] Click toggle
- [ ] Switch changes state

### Save Settings
- [ ] Make changes to settings (slider, toggles)
- [ ] Click "Save Settings" button
- [ ] Loading appears briefly
- [ ] Toast notification appears (green)
- [ ] Says "Settings saved successfully!"

### Account Information
- [ ] Username displayed correctly
- [ ] Email displayed correctly (demo@example.com)
- [ ] Member Since date shown
- [ ] Protection Status shows "Active"
- [ ] Gmail Status shows "Not Connected"
- [ ] "Connect Gmail Account" button visible

### Connect Gmail
- [ ] Click "Connect Gmail Account" button
- [ ] Loading appears briefly
- [ ] Toast notification appears
- [ ] Shows message about Gmail connection
  - (Currently: "Google authentication not yet configured")

---

## 🚪 Logout Tests

### Logout Process
- [ ] Scroll to bottom of sidebar
- [ ] "Logout" button visible with icon
- [ ] Click "Logout" button
- [ ] Confirmation dialog appears: "Are you sure you want to logout?"
- [ ] Click "Cancel" → stays logged in
- [ ] Click "Logout" again
- [ ] Click "OK" → logs out
- [ ] Redirected to login page (login.html)
- [ ] Try to go back to dashboard directly: http://localhost:5001/index.html
- [ ] Automatically redirected to login page (protected)

---

## 🎨 UI/UX Tests

### Toast Notifications
- [ ] Perform any action (add whitelist, scan, etc.)
- [ ] Toast notification slides in from right
- [ ] Has icon matching type (check, warning, error, info)
- [ ] Has appropriate color (green, red, orange, blue)
- [ ] Displays for ~4 seconds
- [ ] Slides out to the right
- [ ] Disappears

### Loading States
- [ ] Click "Scan Now"
- [ ] Full-screen overlay appears
- [ ] Spinner animation visible
- [ ] Text "Scanning emails..." visible
- [ ] After completion, overlay fades out

### Modals
- [ ] Open any modal (Add Whitelist)
- [ ] Modal background darkens screen
- [ ] Modal box centered on screen
- [ ] Click outside modal → modal closes
- [ ] Open modal again
- [ ] Click X button → modal closes

### Forms
- [ ] Click in any input field
- [ ] Border turns purple (focus state)
- [ ] Shadow appears around field
- [ ] Enter invalid email
- [ ] Get validation error
- [ ] Enter valid email
- [ ] Error clears

### Responsive Design
- [ ] Resize browser window smaller
- [ ] UI adjusts appropriately
- [ ] No horizontal scrollbars
- [ ] Text remains readable
- [ ] Buttons remain clickable

---

## 🔒 Security Tests

### Authentication Protection
- [ ] Open browser in incognito/private mode
- [ ] Try to access: http://localhost:5001/index.html
- [ ] Automatically redirected to login
- [ ] Cannot access dashboard without login

### Token Validation
- [ ] Login successfully
- [ ] Open DevTools (F12)
- [ ] Go to Application tab → Local Storage
- [ ] Find `authToken` entry
- [ ] Delete it
- [ ] Try to navigate to any page
- [ ] Automatically redirected to login

### API Protection
- [ ] Open DevTools (F12) → Network tab
- [ ] Perform any action (scan, add whitelist, etc.)
- [ ] Find the API request in Network tab
- [ ] Check Request Headers
- [ ] Should include: `Authorization: Bearer [token]`
- [ ] Check Response
- [ ] Should return data (status 200)

---

## 🎯 Final Verification

### All Buttons Work
- [ ] ✅ Add Whitelist button → Opens modal, saves entry
- [ ] ✅ Add Blacklist button → Opens modal, saves entry
- [ ] ✅ Connect Gmail button → Shows message/loading
- [ ] ✅ Save Settings button → Saves and shows notification
- [ ] ✅ Scan Now button → Triggers scan with loading
- [ ] ✅ Delete Email button → Removes email
- [ ] ✅ Block Sender button → Adds to blacklist
- [ ] ✅ View Details button → Opens modal
- [ ] ✅ Remove buttons → Remove from lists
- [ ] ✅ Logout button → Logs out with confirmation

### All Pages Accessible
- [ ] ✅ Dashboard page loads
- [ ] ✅ Flagged Emails page loads
- [ ] ✅ Reports page loads
- [ ] ✅ Whitelist & Blacklist page loads
- [ ] ✅ Settings page loads

### All Features Work
- [ ] ✅ Login/logout works
- [ ] ✅ Authentication protects pages
- [ ] ✅ Statistics display correctly
- [ ] ✅ Email scanning works
- [ ] ✅ Whitelist management works
- [ ] ✅ Blacklist management works
- [ ] ✅ Settings save correctly
- [ ] ✅ Toast notifications appear
- [ ] ✅ Loading states show
- [ ] ✅ Modals open/close

---

## 🎉 Success Criteria

If you checked ✅ all items above, then:

**🎊 EVERYTHING IS WORKING PERFECTLY! 🎊**

You have a **fully functional, secure email threat detection system** with:
- Complete authentication system
- All buttons working as expected
- Beautiful UI with notifications
- Protected API endpoints
- Professional user experience

---

## 📝 Notes

Record any issues found here:

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

---

## 🆘 If Something Doesn't Work

1. **Hard refresh the browser**: Ctrl+Shift+R (Cmd+Shift+R on Mac)
2. **Clear browser cache and localStorage**
3. **Restart the backend**: Stop with Ctrl+C, then `python3 web_backend.py`
4. **Check browser console**: F12 → Console tab for errors
5. **Check backend terminal**: Look for Python errors
6. **Read documentation**: AUTHENTICATION_GUIDE.md and TROUBLESHOOTING.md

---

## ✅ Testing Complete!

Date: ________________

Tested by: ________________

Overall result: ☐ Pass  ☐ Needs fixes

Notes: _______________________________________________
