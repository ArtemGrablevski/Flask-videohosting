import os
import dotenv


dotenv.load_dotenv(".env")


class Config:
    # Base settings
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    SECURITY_PASSWORD_SALT = os.environ["SECURITY_PASSWORD_SALT"]
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024

    # Mail settings
    GMAIL_PASSWORD = os.environ["GMAIL_PASSWORD"]
    GMAIL_ADRESS = os.environ["GMAIL_ADRESS"]
    MAIL_HOST = "smtp.gmail.com"
    MAIL_PORT = 587