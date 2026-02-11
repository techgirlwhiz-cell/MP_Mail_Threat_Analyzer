# 🔧 Troubleshooting Guide

## "Access to localhost was denied" Error

This error means the Flask web server isn't running. Here's how to fix it:

---

## ✅ SOLUTION (Easy Way)

### Run this command in Terminal:

```bash
cd "/Users/desrine/Documents/Major Project_V1"
./start_dashboard.sh
```

**That's it!** The script will:
1. ✓ Activate the virtual environment
2. ✓ Start the web server
3. ✓ Show you the URL to open

---

## 🔧 Manual Steps (If Script Doesn't Work)

### Step 1: Open Terminal

Open Terminal app on your Mac

### Step 2: Navigate to Project

```bash
cd "/Users/desrine/Documents/Major Project_V1"
```

### Step 3: Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt.

### Step 4: Start the Server

```bash
python3 web_backend.py
```

### Step 5: Open Browser

Navigate to one of these URLs:
- **http://localhost:5000**
- **http://127.0.0.1:5000**

---

## 🐛 Common Issues & Solutions

### Issue 1: "Permission Denied" when running script

**Solution:**
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

### Issue 2: "Port 5000 already in use"

**Solution:** Kill the process using port 5000:
```bash
lsof -ti:5000 | xargs kill -9
```

Then start again:
```bash
./start_dashboard.sh
```

### Issue 3: "Module not found" errors

**Solution:** Install dependencies in virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 4: Browser shows "Can't connect"

**Check if server is running:**
```bash
# Open a new terminal window and run:
curl http://localhost:5000
```

If you get HTML output, server is running but browser might be blocking it.

**Try these URLs:**
- http://localhost:5000
- http://127.0.0.1:5000
- http://0.0.0.0:5000

### Issue 5: Server starts but immediately stops

**Check for errors in the terminal output.**

Common causes:
- Missing dependencies → Run: `pip install flask flask-cors`
- Python version too old → Need Python 3.8+
- Port conflict → Change port in `web_backend.py`

---

## 📋 Step-by-Step Checklist

- [ ] Open Terminal
- [ ] Navigate to project: `cd "/Users/desrine/Documents/Major Project_V1"`
- [ ] Run script: `./start_dashboard.sh`
- [ ] Wait for "Running on http://..." message
- [ ] Open browser to http://localhost:5000
- [ ] See the purple gradient dashboard!

---

## 🔍 Verify Installation

Check if everything is installed correctly:

```bash
cd "/Users/desrine/Documents/Major Project_V1"
source venv/bin/activate
python3 -c "import flask; print('Flask OK')"
python3 -c "import flask_cors; print('Flask-CORS OK')"
```

Both should print "OK". If not, run:
```bash
pip install flask flask-cors
```

---

## 📱 After Server Starts

You should see output like this:

```
==========================================
🚀 Email Threat Protection Dashboard
==========================================

Starting server...

✓ Demo user created with sample data

✓ Server ready!

📱 Open your browser and go to:
   http://localhost:5000

Press Ctrl+C to stop the server
==========================================

 * Serving Flask app 'web_backend'
 * Debug mode: on
WARNING: This is a development server.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

**Now open your browser** to http://localhost:5000

---

## 🎯 What You Should See

When it works, you'll see:
- **Purple gradient sidebar** on the left
- **White dashboard** in the center
- **4 colorful stat cards** at the top
- **Protection circle** showing 95%
- **Recent threats list**

If you see this → **Success!** 🎉

---

## 🆘 Still Not Working?

### Check These:

1. **Is Terminal showing errors?**
   - Read the error message
   - Google the error if needed
   - Check if Python 3.8+ is installed: `python3 --version`

2. **Is the server actually running?**
   - You should see "Running on http://..." in Terminal
   - Don't close the Terminal window
   - The server needs to keep running

3. **Is your browser blocking localhost?**
   - Try a different browser (Chrome, Firefox, Safari)
   - Try http://127.0.0.1:5000 instead
   - Check if browser has security settings blocking local servers

4. **Are you on the right port?**
   - Default is port 5000
   - Check Terminal output for the actual port
   - Use the URL shown in Terminal

5. **Firewall blocking?**
   - Check macOS firewall settings
   - Allow Python to accept connections
   - System Preferences → Security & Privacy → Firewall

---

## 💡 Pro Tips

### Keep Terminal Open
The Terminal window with the server **must stay open**. Don't close it!

### Stop the Server
Press `Ctrl+C` in the Terminal to stop the server.

### Restart the Server
If you make changes to code:
1. Stop server (Ctrl+C)
2. Run `./start_dashboard.sh` again

### View Logs
All server activity shows in the Terminal window. Watch for errors here.

---

## 🎓 Understanding the Error

**"Access to localhost was denied"** means:

1. **Server not running** (most common)
   → Start it with `./start_dashboard.sh`

2. **Wrong port**
   → Check Terminal for actual port number

3. **Browser blocking**
   → Try different browser or http://127.0.0.1:5000

4. **Firewall blocking**
   → Allow Python in firewall settings

---

## ✅ Quick Test

Run this to test if everything works:

```bash
cd "/Users/desrine/Documents/Major Project_V1"
./start_dashboard.sh
```

Wait 5 seconds, then open http://localhost:5000

If you see the purple dashboard → **Working!** 🎉

---

## 📞 Need More Help?

1. Read the error message in Terminal carefully
2. Check `WEB_UI_START.md` for more details
3. Verify Flask is installed: `pip list | grep -i flask`
4. Try running in a fresh Terminal window

---

**Remember:** The server must be running in Terminal for the website to work!
