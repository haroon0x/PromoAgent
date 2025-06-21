import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from src.utils.config import get_brand_instructions
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")

def send_gmail_notification(subject: str, body: str, to_email: str = None):
    """
    Send an email notification via Gmail SMTP.
    """
    if to_email is None:
        to_email = NOTIFY_EMAIL
    if not (GMAIL_USER and GMAIL_APP_PASSWORD and to_email):
        raise ValueError("Gmail credentials or recipient email not set in environment.")

    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}") 