import os
import random
import smtplib
import string
from email.mime.text import MIMEText

otp_store = {}


# Simulated temporary OTP store (for demo; use Redis or DB in prod)


def generate_otp(length=4):
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(to_email, otp):
    message = MIMEText(f"Your OTP is: {otp}")
    from_email = os.getenv("from_email_id")  # "support@smarthealapp.com"
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = 'Smart-Heal, Password Reset OTP'
    print(f"Sending OTP {otp} to {to_email}")
    smtp_server = "smtpout.secureserver.net"  # 'mail.firsttoothclinic.com'
    server = smtplib.SMTP_SSL(smtp_server, 465, timeout=30)
    status_code, response = server.ehlo()
    print(f"SMTP server response: {status_code} {response.decode()}")
    # status_code, response = server.starttls()
    # print(f"Start TLS connection: {status_code} {response.decode()}")
    status_code, response = server.login(from_email, os.getenv("email_password"))
    print(f"Login response: {status_code} {response.decode()}")
    server.sendmail(from_email, to_email, message.as_string())
    server.quit()


# def send_email_reset_link(email: str, token: str):
#     to_email = email
#     sub = "check"
#     body = "check"
#     from_email = ""
#     from_password = ""
#
#     msg = EmailMessage()
#     msg['Subject'] = sub
#     msg['From'] = from_email
#     msg['To'] = to_email
#     msg.set_content(body)
#
#     try:
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#             server.login(from_email, from_password)
#             server.send_message(msg)
#             print(f"Sending reset link to {email} with token {token}")
#             print(f"Reset link sent to {email}")
#     except Exception as e:
#         print(f"Failed to send email: {e}")


# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
#
# # Replace with your SendPulse SMTP credentials
# smtp_server = "smtp.sendpulse.com"
# smtp_port = 587
# smtp_username = "madhur.mj04@gmail.com"  # Usually the email you signed up with
# smtp_password = "G1@madmun"  # You’ll find this in SMTP settings
#
# # Email details
# sender_email = smtp_username
# receiver_email = "madhur.munjal@yahoo.in"
# subject = "Hello from SendPulse and Python"
# body = "This is a test email sent using SendPulse SMTP server and Python!"
#
# # Create the message
# message = MIMEMultipart()
# message["From"] = sender_email
# message["To"] = receiver_email
# message["Subject"] = subject
# message.attach(MIMEText(body, "plain"))
#
# # Send the email
# try:
#     with smtplib.SMTP(smtp_server, smtp_port) as server:
#         server.starttls()
#         server.login(smtp_username, smtp_password)
#         server.sendmail(sender_email, receiver_email, message.as_string())
#         print("✅ Email sent successfully!")
# except Exception as e:
#     print(f"❌ Failed to send email: {e}")

# send_email_reset_link("madhur.munjal@yahoo.in", "abc")

# def send_email():
#     import smtplib
#     from email.mime.text import MIMEText
#     from email.mime.multipart import MIMEMultipart
#
#
#     # Email credentials
#     sender_email = "smartheal04@gmail.com"
#     receiver_email = "madhur.munjal@yahoo.in"
#     app_password = "your_app_password"  # Use an app password, not your regular Gmail password
#
#     # Compose the message
#     message = MIMEMultipart()
#     message["From"] = sender_email
#     message["To"] = receiver_email
#     message["Subject"] = "Hello from Python"
#
#     body = "This is a test email sent from Python!"
#     message.attach(MIMEText(body, "plain"))
#
#     # Send the email
#     try:
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login(sender_email, app_password)
#             server.sendmail(sender_email, receiver_email, message.as_string())
#             print("Email sent successfully!")
#     except Exception as e:
#         print(f"Failed to send email: {e}")
