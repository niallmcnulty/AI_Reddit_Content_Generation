import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    WP_URL = os.getenv('WP_URL')
    WP_USERNAME = os.getenv('WP_USERNAME')
    WP_PASSWORD = os.getenv('WP_PASSWORD')
