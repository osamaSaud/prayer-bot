import os
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Prayer API Configuration
PRAYER_API_URL = "http://api.aladhan.com/v1/timingsByCity"
PRAYER_API_PARAMS = {
    'city': 'Riyadh',
    'country': 'Saudi Arabia',
    'method': 4
} 