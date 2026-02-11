"""
Main Application Entry Point
Starts with login window, then transitions to main dashboard.
"""

import tkinter as tk
import customtkinter as ctk
from login_window import LoginWindow
from phishing_gui_main import PhishingDetectionDashboard


def start_dashboard(username):
    """Start the main dashboard after successful login."""
    # Close login window
    try:
        root = tk._default_root
        if root:
            root.destroy()
    except:
        pass
    
    # Create new window for dashboard
    root = tk.Tk()
    dashboard = PhishingDetectionDashboard(root, username)
    root.mainloop()


def main():
    """Main entry point."""
    # Set appearance mode
    ctk.set_appearance_mode("light")
    
    # Create root window for login
    root = tk.Tk()
    login = LoginWindow(root, start_dashboard)
    root.mainloop()


if __name__ == "__main__":
    main()

