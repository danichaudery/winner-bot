import os
import smtplib
from email.mime.text import MIMEText


def send_email_alert(to_email: str, subject: str, body: str) -> None:
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "")
    password = os.getenv("SMTP_PASSWORD", "")
    if not username or not password:
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = username
    msg["To"] = to_email
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(username, [to_email], msg.as_string())

