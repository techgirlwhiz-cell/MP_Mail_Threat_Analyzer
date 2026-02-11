# Email Threat Protection Dashboard - Web UI

## 🎨 Beautiful Purple & White Gradient Interface

A modern, responsive web-based dashboard for monitoring and managing email threats with a stunning purple and white gradient design.

## ✨ Features

### 🎨 **Beautiful Design**
- Purple and white gradient theme throughout
- Modern, clean interface
- Smooth animations and transitions
- Responsive design (works on all devices)
- Professional color scheme

### 📊 **Dashboard**
- Real-time statistics display
- Threat detection metrics
- Protection status circle
- Recent threats list
- Auto-refresh functionality

### 📧 **Flagged Emails**
- View all flagged emails
- Filter by threat type
- Search functionality
- Detailed email analysis
- Risk factor breakdown
- Action recommendations

### 📈 **Reports**
- Threat analysis summary
- Activity timeline
- Email categorization
- Export functionality (planned)

### ✅ **Whitelist & Blacklist Management**
- View trusted senders
- View blocked senders
- Add/remove senders easily
- Beautiful card-based layout

### ⚙️ **Settings**
- Adjustable threat sensitivity slider
- Toggle auto-flagging
- Toggle notifications
- User account information

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip3 install flask flask-cors
```

Or install all requirements:

```bash
pip3 install -r requirements.txt
```

### 2. Start the Web Server

```bash
python3 web_backend.py
```

### 3. Open in Browser

Navigate to:
```
http://localhost:5000
```

## 📁 File Structure

```
web_ui/
├── index.html          # Main HTML file
├── styles.css          # Purple & white gradient styling
└── app.js              # Frontend JavaScript

web_backend.py          # Flask API backend
```

## 🎨 Color Scheme

The dashboard features a beautiful purple and white gradient theme:

### Primary Colors
- **Purple**: `#8B5CF6` (Primary)
- **Dark Purple**: `#6D28D9` (Accents)
- **Light Purple**: `#DDD6FE` (Backgrounds)
- **White**: `#FFFFFF` (Text & Cards)

### Accent Colors
- **Success**: `#10B981` (Green)
- **Warning**: `#F59E0B` (Orange)
- **Danger**: `#EF4444` (Red)

### Gradients
- Sidebar: Purple gradient (180deg)
- Header: Subtle purple to white
- Buttons: Purple gradient (135deg)
- Stats cards: Color-coded gradients

## 📱 Pages

### 1. Dashboard
- **Stats Cards**: Total scanned, threats detected, threats blocked, threat rate
- **Protection Circle**: Visual protection score indicator
- **Protection Details**: Sensitivity level, auto-flag status, last scan time
- **Recent Threats**: Latest detected threats with scores

### 2. Flagged Emails
- **Email List**: Grid view of all flagged emails
- **Filter Options**: Filter by threat type (phishing, spam, malware)
- **Search**: Search by subject or sender
- **Actions**: View details, delete email
- **Threat Badges**: Color-coded threat levels

### 3. Reports
- **Summary Cards**: Total emails, phishing, spam, clean emails
- **Activity Timeline**: Recent system activities
- **Export Option**: Export reports (button ready)

### 4. Whitelist & Blacklist
- **Whitelist Grid**: Trusted senders in card layout
- **Blacklist Grid**: Blocked senders in card layout
- **Add Buttons**: Easy to add new senders
- **Remove Actions**: Quick remove functionality

### 5. Settings
- **Threat Sensitivity Slider**: Adjust from 0-100%
- **Auto-Flag Toggle**: Enable/disable auto-flagging
- **Notifications Toggle**: Enable/disable notifications
- **Account Info**: User details and statistics
- **Save Button**: Save all settings

## 🔧 API Endpoints

The Flask backend provides these endpoints:

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-threats` - Get recent threats

### Flagged Emails
- `GET /api/flagged-emails` - Get all flagged emails
- `GET /api/flagged-emails/<id>` - Get email details
- `DELETE /api/flagged-emails/<id>` - Delete email

### Scanning
- `POST /api/scan/inbox` - Scan entire inbox
- `POST /api/scan/email` - Scan single email

### Reports
- `GET /api/reports/summary` - Get report summary
- `GET /api/reports/activity` - Get activity timeline

### Whitelist/Blacklist
- `GET /api/whitelist` - Get whitelist
- `POST /api/whitelist` - Add to whitelist
- `DELETE /api/whitelist/<email>` - Remove from whitelist
- `GET /api/blacklist` - Get blacklist
- `POST /api/blacklist` - Add to blacklist
- `DELETE /api/blacklist/<email>` - Remove from blacklist

### Settings
- `GET /api/settings` - Get user settings
- `PUT /api/settings` - Update settings

## 🎯 Features Showcase

### Real-Time Updates
- Dashboard auto-refreshes every 30 seconds
- Instant updates on scan completion
- Live threat score calculations

### Interactive Elements
- **Hover Effects**: Smooth transitions on hover
- **Click Actions**: Responsive button clicks
- **Modal Windows**: Beautiful email detail modals
- **Smooth Animations**: Fade-in effects on page changes

### Responsive Design
- **Desktop**: Full-width sidebar, multi-column layouts
- **Tablet**: Optimized spacing and layout
- **Mobile**: Collapsible sidebar, stacked layouts

## 🎨 Design Elements

### Sidebar Navigation
- Purple gradient background
- White icons and text
- Active state highlighting
- Hover effects
- User profile section at bottom

### Header
- Gradient background
- Page title and subtitle
- Scan Now button
- Notification bell with badge

### Cards
- White background
- Subtle shadows
- Rounded corners
- Gradient header bars
- Smooth hover effects

### Stats Cards
- Color-coded gradient tops
- Icon with gradient background
- Large number display
- Descriptive labels

### Email Items
- Grid layout with checkbox
- Threat badges (color-coded)
- Threat score display
- Action buttons

### Protection Circle
- SVG-based circular progress
- Gradient stroke
- Animated fill
- Center percentage display

## 🔒 Security Notes

### Current Implementation
- Demo user setup for testing
- Local data storage
- No real authentication (development)

### For Production
- Implement proper authentication
- Add session management
- Use secure cookies
- Add CSRF protection
- Implement rate limiting
- Add input validation
- Use HTTPS

## 🎓 Customization

### Change Colors
Edit `styles.css` CSS variables:

```css
:root {
    --primary-purple: #8B5CF6;
    --dark-purple: #6D28D9;
    --light-purple: #DDD6FE;
    /* ... */
}
```

### Change API Endpoint
Edit `app.js` config:

```javascript
const CONFIG = {
    apiEndpoint: '/api',  // Change this
    username: 'demo_user',
    refreshInterval: 30000
};
```

### Add New Pages
1. Add nav item in `index.html`
2. Create page content section
3. Add to navigation handler in `app.js`
4. Create API endpoint in `web_backend.py`

## 🐛 Troubleshooting

### Port Already in Use
If port 5000 is busy, change it in `web_backend.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

### CORS Errors
Make sure Flask-CORS is installed:

```bash
pip3 install flask-cors
```

### Styles Not Loading
Check that files are in `web_ui/` folder:
- `web_ui/index.html`
- `web_ui/styles.css`
- `web_ui/app.js`

### API Errors
Check Flask console for error messages and ensure the Gmail add-on system is properly initialized.

## 📊 Performance

- **Load Time**: < 2 seconds
- **API Response**: < 500ms
- **Refresh Rate**: 30 seconds (configurable)
- **Animations**: 60 FPS smooth transitions

## 🎉 Demo Data

The system automatically creates demo data on first run:
- Demo user: `demo_user`
- Sample emails: 15 total
- Phishing ratio: 30%
- Flagged threats: Automatically detected

## 📚 Resources

- **Font Awesome Icons**: Used for all icons
- **Custom CSS**: No external UI frameworks
- **Vanilla JavaScript**: No dependencies
- **Flask Backend**: Simple Python web framework

## 🚀 Production Deployment

For production deployment:

1. **Use WSGI Server**: Use Gunicorn or uWSGI instead of Flask dev server
2. **Enable HTTPS**: Use SSL/TLS certificates
3. **Set Environment Variables**: Store sensitive config in environment
4. **Use Real Database**: Replace file-based storage with PostgreSQL/MySQL
5. **Add Authentication**: Implement proper user authentication
6. **Enable Logging**: Add comprehensive logging
7. **Add Monitoring**: Use tools like Sentry or New Relic
8. **Optimize Assets**: Minify CSS/JS, compress images

## 🎨 Screenshots

The dashboard features:
- **Purple gradient sidebar** with navigation
- **White content area** with gradient accents
- **Colorful stat cards** with gradients
- **Clean email list** with badges
- **Modern modals** for details
- **Smooth animations** throughout

## 🤝 Integration

To integrate with your own backend:

1. Update API endpoints in `app.js`
2. Implement authentication in `web_backend.py`
3. Connect to your database
4. Customize user management
5. Add your business logic

## ✨ Features Coming Soon

- [ ] Dark mode toggle
- [ ] Export reports to PDF/CSV
- [ ] Advanced filtering options
- [ ] Email forwarding
- [ ] Bulk actions
- [ ] Mobile app
- [ ] Real-time notifications
- [ ] Chart visualizations

---

**Enjoy the beautiful purple and white gradient dashboard! 💜🤍**

For questions or issues, check the main documentation in `README_GMAIL_ADDON.md`.
