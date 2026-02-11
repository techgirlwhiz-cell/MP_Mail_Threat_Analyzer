# GUI Application with Login & Dashboard

## 🎨 New Features

The phishing detection system now includes:

### 🔐 Login & Signup System
- Beautiful purple gradient themed login window
- User registration and authentication
- Secure password hashing
- Session management

### 📊 Interactive Dashboard
- **Analysis Tab**: Upload CSV, analyze emails, view results
- **Results Summary Tab**: Visual graphs showing:
  - Pie chart of phishing vs legitimate emails
  - Bar chart with email counts
- **History Tab**: Complete history of all your analyses with:
  - Timestamp for each session
  - Total emails analyzed
  - Phishing/Legitimate breakdown
  - Model and file information

## 🚀 How to Run

### Start the Application

```bash
python app.py
```

This will:
1. Show the login/signup window
2. After login, open the main dashboard
3. Allow you to analyze emails and view history

### First Time Setup

1. **Run the application**:
   ```bash
   python app.py
   ```

2. **Create an account**:
   - Click on "Sign Up" tab
   - Enter username, email (optional), and password
   - Click "Create Account"

3. **Login**:
   - Enter your username and password
   - Click "Sign In"

4. **Start analyzing**:
   - Load a model (`.pkl` file)
   - Upload a CSV file
   - Click "Analyze Emails"
   - View results in the tabs!

## 📋 Features Overview

### Login Window
- **Purple gradient header** with modern design
- **Tabbed interface** for Login/Signup
- **Form validation** and error handling
- **Secure authentication** with password hashing

### Main Dashboard

#### Analysis Tab
- Model loading
- CSV file upload
- Email analysis with progress tracking
- Detailed results display
- Export results to CSV

#### Results Summary Tab
- **Pie Chart**: Visual breakdown of phishing vs legitimate
- **Bar Chart**: Email counts by category
- **Real-time updates** after each analysis

#### History Tab
- **Complete session history** for all analyses
- **Statistics** for each session:
  - Date and time
  - Total emails
  - Phishing count and percentage
  - Legitimate count and percentage
  - Model used
  - File analyzed
- **Scrollable view** for easy browsing

## 🎨 Design Features

- **Purple & White Theme**: Modern gradient design
- **Professional UI**: Clean, intuitive interface
- **Responsive Layout**: Adapts to window size
- **Color-coded Results**: Easy to understand visualizations
- **Smooth Animations**: Progress bars and transitions

## 📁 File Structure

- `app.py` - Main entry point (starts with login)
- `login_window.py` - Login/signup interface
- `user_auth.py` - Authentication system
- `phishing_gui_main.py` - Main dashboard with tabs
- `users.json` - User data (created automatically)
- `sessions.json` - Session history (created automatically)

## 🔒 Security

- Passwords are hashed using SHA256
- User data stored locally in JSON files
- Session tracking for analysis history

## 💡 Tips

- **Multiple Users**: Each user has their own analysis history
- **Session Tracking**: All analyses are automatically saved
- **Graph Updates**: Graphs update automatically after analysis
- **History View**: Scroll through all your past analyses
- **Export**: Save results to CSV for external use

## 🆘 Troubleshooting

**Can't login?**
- Make sure you've created an account first
- Check username and password spelling
- Try creating a new account

**Graphs not showing?**
- Run an analysis first
- Check that you have results from an analysis
- Make sure matplotlib is installed: `pip install matplotlib`

**History empty?**
- History appears after your first analysis
- Each analysis creates a new history entry
- History is saved per user account

## 📊 Example Workflow

1. **Launch**: `python app.py`
2. **Sign Up**: Create account with username/password
3. **Login**: Sign in with your credentials
4. **Load Model**: Click "Load Model" and select `.pkl` file
5. **Upload CSV**: Click "Upload CSV File" and select your data
6. **Analyze**: Click "Analyze Emails" and wait for results
7. **View Results**: 
   - See detailed results in Analysis tab
   - Check graphs in Results Summary tab
   - Review history in History tab
8. **Export**: Save results to CSV if needed

Enjoy your beautiful, modern phishing detection system! 🎉

