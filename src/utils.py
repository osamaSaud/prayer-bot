from datetime import datetime
import requests
from config import PRAYER_API_URL, PRAYER_API_PARAMS, logger

def convert_to_12_hour(time_str):
    """Convert 24-hour format to 12-hour format with AM/PM"""
    time_obj = datetime.strptime(time_str, '%H:%M')
    return time_obj.strftime('%I:%M %p')

def get_prayer_times():
    """Fetch prayer times from the API"""
    try:
        response = requests.get(PRAYER_API_URL, params=PRAYER_API_PARAMS)
        data = response.json()
        timings = data['data']['timings']
        return {
            'الفجر': timings['Fajr'],
            'الشروق': timings['Sunrise'],
            'الظهر': timings['Dhuhr'],
            'العصر': timings['Asr'],
            'المغرب': timings['Maghrib'],
            'العtraشاء': timings['Isha']
        }
    except Exception as e:
        logger.error(f"Error fetching prayer times: {e}")
        return None 