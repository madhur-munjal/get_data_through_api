import smtplib
from email.message import EmailMessage


def send_email_reset_link(email: str, token: str):
    to_email = email
    sub = ""
    body = ""
    from_email = "smartheal04@gmail.com"
    from_password = "check04"

    msg = EmailMessage()
    msg['Subject'] = sub
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, from_password)
            server.send_message(msg)
            print(f"Sending reset link to {email} with token {token}")
            print(f"Reset link sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
