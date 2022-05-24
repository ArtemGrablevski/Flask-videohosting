import smtplib
from email.mime.text import MIMEText
from loguru import logger
from .app import app


def send_verification_email(target: str, link: str) -> None:
    message = f"""
        <html>
        <body>
            <h1>Click here to confirm your email on <i style="color: rgb(94, 162, 252)">Sphere</i> :</h1>
            <h1 align="center"> <a href={link}>Confirm</a> </h1>
        </body>
        </html>
        """
    try:
        msg = MIMEText(message, "html")
        msg["Subject"] = "Verify your email"
        msg["Sender"] = "Artem"

        sender = app.config["GMAIL_ADRESS"]
        password = app.config["GMAIL_PASSWORD"]

        server = smtplib.SMTP(app.config["MAIL_HOST"], app.config["MAIL_PORT"])
        server.starttls()

        server.login(sender, password)
        server.sendmail(sender, target, msg.as_string())
        logger.info(f"Succesfully sent verification email to {target}")
    except Exception as ex:
        logger.error(f"{ex} occured while sending verification email to {target}")


