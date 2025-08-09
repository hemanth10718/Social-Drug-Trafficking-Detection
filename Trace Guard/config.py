import os
from dotenv import load_dotenv

load_dotenv()
import os
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env file
class Config:

    INSTAGRAM_USERNAME = os.getenv('purnima0_1')
    INSTAGRAM_PASSWORD = os.getenv('purni-12345')
    TWITTER_BEARER_TOKEN = os.getenv('AAAAAAAAAAAAAAAAAAAAAFsCvwEAAAAAmRtt%2BKbi4qC4oIySxMxuRJrYqOk%3DmIfQXIZedqKBMWspIQAWU2j5HG49oiRjEvSXB4gSqOwRm1fEMB')
    TELEGRAM_API_ID = os.getenv('22279321')
    TELEGRAM_API_HASH = os.getenv('1949c2ca051e57991b69be18b7c973ad')


    # Flask secret key


    # Paths
    DATA_DIR = 'data'
    REPORTS_DIR = 'reports'
    REFERENCE_DATA = 'data/reference_data.csv'
    
    # Proxy settings
    PROXY_FILE = 'valid_proxies.txt'

    @classmethod
    def verify(cls):
        missing = []
        if not cls.INSTAGRAM_USERNAME: missing.append('INSTAGRAM_USERNAME')
        if not cls.INSTAGRAM_PASSWORD: missing.append('INSTAGRAM_PASSWORD')
        if not cls.TWITTER_BEARER_TOKEN: missing.append('TWITTER_BEARER_TOKEN')
        if not cls.TELEGRAM_API_ID: missing.append('TELEGRAM_API_ID')
        if not cls.TELEGRAM_API_HASH: missing.append('TELEGRAM_API_HASH')
        
        if missing:
            raise ValueError(f"Missing configuration: {', '.join(missing)}")