import telebot
from datetime import datetime, timedelta
import pytz
import schedule
import time
from threading import Thread
from config import BOT_TOKEN, CHAT_ID, logger
from utils import get_prayer_times, convert_to_12_hour
import os

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['time'])
def handle_time_command(message):
    bot.reply_to(message, "سأرسل لك جدول الصلاة بعد 60 ثانية ⏳")
    Thread(target=delayed_schedule, args=(message.chat.id,)).start()

@bot.message_handler(commands=['next'])
def handle_next_command(message):
    bot.reply_to(message, "سأخبرك عن موعد الصلاة القادمة بعد 60 ثانية ⏳")
    Thread(target=delayed_next_prayer, args=(message.chat.id,)).start()

def delayed_schedule(chat_id):
    time.sleep(60)
    prayer_times = get_prayer_times()
    if prayer_times:
        message = "مواقيت الصلاة في الرياض لهذا اليوم:\n\n"
        for prayer, prayer_time in prayer_times.items():
            time_12hr = convert_to_12_hour(prayer_time)
            message += f"{prayer}: {time_12hr}\n📿"
        bot.send_message(chat_id, message)

def delayed_next_prayer(chat_id):
    time.sleep(60)
    prayer_times = get_prayer_times()
    if prayer_times:
        now = datetime.now(pytz.timezone('Asia/Riyadh'))
        current_time = now.strftime('%H:%M')
        
        next_prayer = None
        time_remaining = None
        found_next = False
        
        # First check today's remaining prayers
        for prayer, prayer_time in prayer_times.items():
            if prayer_time > current_time:
                next_prayer = prayer
                current_dt = now
                prayer_dt = datetime.strptime(prayer_time, '%H:%M').replace(
                    year=now.year,
                    month=now.month,
                    day=now.day
                )
                
                time_diff = (prayer_dt - current_dt).total_seconds()
                minutes_remaining = int(time_diff // 60)
                hours = minutes_remaining // 60
                minutes = minutes_remaining % 60
                
                if hours > 0:
                    time_remaining = f"{hours} ساعة و {minutes} دقيقة"
                else:
                    time_remaining = f"{minutes} دقيقة"
                found_next = True
                break
        
        # If no remaining prayers today, get first prayer of tomorrow
        if not found_next:
            first_prayer = list(prayer_times.items())[0]  # Get first prayer (Fajr)
            next_prayer = first_prayer[0]
            
            current_dt = now
            tomorrow = now.replace(hour=0, minute=0) + timedelta(days=1)
            prayer_dt = datetime.strptime(first_prayer[1], '%H:%M').replace(
                year=tomorrow.year,
                month=tomorrow.month,
                day=tomorrow.day
            )
            
            time_diff = (prayer_dt - current_dt).total_seconds()
            minutes_remaining = int(time_diff // 60)
            hours = minutes_remaining // 60
            minutes = minutes_remaining % 60
            
            time_remaining = f"{hours} ساعة و {minutes} دقيقة"
        
        message = f"الصلاة القادمة هي {next_prayer} ⏰\n"
        message += f"باقي {time_remaining} على وقت الصلاة 🕌"
        bot.send_message(chat_id, message)

def send_daily_schedule():
    prayer_times = get_prayer_times()
    if prayer_times:
        message = "مواقيت الصلاة في الرياض لهذا اليوم:\n\n"
        for prayer, time in prayer_times.items():
            time_12hr = convert_to_12_hour(time)
            message += f"{prayer}: {time_12hr}📿\n"
        bot.send_message(CHAT_ID, message)

def check_prayer_times():
    prayer_times = get_prayer_times()
    if prayer_times:
        current_time = datetime.now(pytz.timezone('Asia/Riyadh')).strftime('%H:%M')
        for prayer, time in prayer_times.items():
            if time == current_time:
                message = f"حان الآن موعد صلاة {prayer}🕌"
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
        
        # Add these lines to handle the polling conflict
        bot.remove_webhook()
        time.sleep(1)
        
        logger.info("Starting bot polling...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
        
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        raise e

if __name__ == "__main__":
    main() 