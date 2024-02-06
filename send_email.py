import os
from email.message import EmailMessage
import ssl
import smtplib
from dotenv import load_dotenv

load_dotenv()

def send_verification_email_to(email_receiver, token):
    email_sender = os.getenv('BOT_EMAIL')
    email_passwort = os.getenv('BOT_PASSWORD')
    subject = "Verification token for Discord server"
    body_template = """
Hello there,
to verify your account on our Discord server, please use the following token:

{}

Best,
Your admin team"""

    body = body_template.format(token)

    em = EmailMessage()
    em["To"] = email_receiver
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'), context=context) as smtp:
        smtp.login(email_sender, email_passwort)
        smtp.sendmail(email_sender, email_receiver, em.as_string())