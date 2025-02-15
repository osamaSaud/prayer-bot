import telebot
from datetime import datetime
import pytz
import schedule
import time
from threading import Thread
from config import BOT_TOKEN, CHAT_ID, logger
from utils import get_prayer_times, convert_to_12_hour

bot = telebot.TeleBot(BOT_TOKEN)

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
    schedule.every().day.at("04:00").do(send_daily_schedule)
    schedule.every().minute.do(check_prayer_times)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

def main():
    try:
        logger.info("Bot started...")
        send_daily_schedule()
        schedule_jobs()
        
        scheduler_thread = Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        while True:
            time.sleep(60)
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        raise e

if __name__ == "__main__":
    main() 