import telebot
import requests
from datetime import datetime
import pytz
import schedule
import time
from threading import Thread
import os
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN', '8033085749:AAHCcJt5qfZG-1WC03Et1SFYiTqP4BxPkFo')
CHAT_ID = os.getenv('CHAT_ID', '872970582')

bot = telebot.TeleBot(BOT_TOKEN)

def convert_to_12_hour(time_str):
    """Convert 24-hour format to 12-hour format with AM/PM"""
    time_obj = datetime.strptime(time_str, '%H:%M')
    return time_obj.strftime('%I:%M %p')

def get_prayer_times():
    url = "http://api.aladhan.com/v1/timingsByCity"
    params = {
        'city': 'Riyadh',
        'country': 'Saudi Arabia',
        'method': 4
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        timings = data['data']['timings']
        return {
            'الفجر': timings['Fajr'],
            'الشروق': timings['Sunrise'],
            'الظهر': timings['Dhuhr'],
            'العصر': timings['Asr'],
            'المغرب': timings['Maghrib'],
            'العشاء': timings['Isha']
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_daily_schedule():
    prayer_times = get_prayer_times()
    if prayer_times:
        message = "🕌 مواقيت الصلاة في الرياض لهذا اليوم:\n\n"
        for prayer, time in prayer_times.items():
            time_12hr = convert_to_12_hour(time)
            message += f"📿 {prayer}: {time_12hr}\n"
        bot.send_message(CHAT_ID, message)

def check_prayer_times():
    prayer_times = get_prayer_times()
    if prayer_times:
        current_time = datetime.now(pytz.timezone('Asia/Riyadh')).strftime('%H:%M')
        for prayer, time in prayer_times.items():
            if time == current_time:
                message = f"🕌 حان الآن موعد صلاة {prayer}"
                bot.send_message(CHAT_ID, message)

def schedule_jobs():
    # Schedule daily prayer times message at 4:00 AM
    schedule.every().day.at("04:00").do(send_daily_schedule)
    
    # Check for prayer times every minute
    schedule.every().minute.do(check_prayer_times)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    try:
        logger.info("Bot started...")
        send_daily_schedule()
        schedule_jobs()
        
        # Start the scheduler
        scheduler_thread = Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(60)
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        raise e