import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from project root
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str):
        if not SMTP_USER or not SMTP_PASSWORD:
            print("WARNING: SMTP credentials (SMTP_USER/SMTP_PASSWORD) not set in .env. Email not sent.")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = SMTP_USER
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(html_content, "html"))

            print(f"Connecting to SMTP: {SMTP_HOST}:{SMTP_PORT}...")
            # Note: Gmail requires App Password if 2FA is on.
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, to_email, msg.as_string())
            
            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    @staticmethod
    def send_verification_email(to_email: str, token: str):
        # Kept for compatibility, though Supabase handles this natively.
        verification_link = f"http://127.0.0.1:8000/auth/verify/{token}"
        subject = "Verify your email - Mood Journal"
        html = f"""
        <h1>Welcome to Mood Journal!</h1>
        <p>Please verify your email address by clicking the link below:</p>
        <a href="{verification_link}">Verify Email</a>
        """
        return EmailService.send_email(to_email, subject, html)

    @staticmethod
    def send_password_reset_email(to_email: str, reset_link: str):
        subject = "Reset your Mood Journal password"
        html = f"""
        <h1>Reset Password</h1>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_link}">Reset Password</a>
        """
        return EmailService.send_email(to_email, subject, html)
