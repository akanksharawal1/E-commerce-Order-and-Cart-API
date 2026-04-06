import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = quote_plus(os.getenv("DB_PASS"))
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
