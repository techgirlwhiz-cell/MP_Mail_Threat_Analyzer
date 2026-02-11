import customtkinter as ctk
from user_auth import UserAuth


class LoginWindow(ctk.CTk):

    def __init__(self, on_login_success):
        super().__init__()

        self.on_login_success = on_login_success
        self.auth = UserAuth()

        self.title("Phishing Detection System - Login")
        self.geometry("400x300")

        ctk.CTkLabel(self, text="Login", font=("Arial", 20)).pack(pady=20)

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email")
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        self.message_label = ctk.CTkLabel(self, text="", text_color="red")
        self.message_label.pack(pady=5)

        ctk.CTkButton(
            self,
            text="Login",
            command=self.login_user
        ).pack(pady=15)

    def login_user(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        success, message = self.auth.login(email, password)

        if success:
            self.destroy()
            self.on_login_success(email)
        else:
            self.message_label.configure(text=message)
