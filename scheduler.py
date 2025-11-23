import asyncio
import os
from datetime import datetime, timedelta, timezone
from services.telegram_bot import application
from services.database import DatabaseService
from dotenv import load_dotenv

load_dotenv()

# Configuration
CHECK_INTERVAL = 60 # Check every minute to be precise with time
USER_TELEGRAM_ID = os.getenv("USER_TELEGRAM_ID") 
STRETCH_INTERVAL_MINUTES = 90  # 1.5 hours
STRETCH_START_HOUR = 10  # 10 AM
STRETCH_END_HOUR = 23  # 11 PM (allows reminder at 11:30 PM if interval matches)

db = DatabaseService()

# Track last stretch reminder time
last_stretch_time = None

async def proactive_loop():
    """Main scheduler loop."""
    global last_stretch_time
    print("Elena Scheduler started.")
    
    # State to prevent double sending in the same minute
    last_sent_date = None
    
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        
        # Get current EST time
        est_offset = timezone(timedelta(hours=-5))
        now = datetime.now(est_offset)
        current_date_str = now.strftime("%Y-%m-%d")
        
        # 9:00 AM Daily Check-in
        if now.hour == 9 and now.minute == 0:
            if last_sent_date != current_date_str:
                await trigger_daily_checkin()
                
                # Check for 3-day body check
                # Simple logic: if day of year is divisible by 3
                day_of_year = now.timetuple().tm_yday
                if day_of_year % 3 == 0:
                    await trigger_body_check()
                
                last_sent_date = current_date_str
        
        # 9:30 AM Breakfast Reminder
        if now.hour == 9 and now.minute == 30:
            await trigger_breakfast_reminder()
        
        # 12:30 PM Lunch Reminder
        if now.hour == 12 and now.minute == 30:
            await trigger_lunch_reminder()
        
        # 6:00 PM Dinner Reminder
        if now.hour == 18 and now.minute == 0:
            await trigger_dinner_reminder()
        
        # 10:25 PM Evening Wind-Down Routine
        if now.hour == 22 and now.minute == 25:
            await trigger_evening_winddown()
        
        # Stretch/Break Reminder (every 1.5 hours during active hours)
        if STRETCH_START_HOUR <= now.hour < STRETCH_END_HOUR:
            if last_stretch_time is None:
                # First stretch reminder of the day
                last_stretch_time = now
                await trigger_stretch_reminder()
            else:
                # Check if 90 minutes have passed
                time_diff = (now - last_stretch_time).total_seconds() / 60
                if time_diff >= STRETCH_INTERVAL_MINUTES:
                    last_stretch_time = now
                    await trigger_stretch_reminder()

async def trigger_daily_checkin():
    """Trigger daily sleep/diet check."""
    if not USER_TELEGRAM_ID or not application:
        return
        
    print("Triggering Elena Daily Check-in...")
    try:
        if not application._initialized:
            await application.initialize()
            
        msg = "Good morning! ☀️ How was your sleep quality last night? And what's the plan for breakfast?"
        
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e:
        print(f"Failed to trigger check-in: {e}")

async def trigger_body_check():
    """Trigger 3-day body check."""
    if not USER_TELEGRAM_ID or not application:
        return
        
    print("Triggering Elena Body Check...")
    try:
        if not application._initialized:
            await application.initialize()
            
        msg = "Time for a body check-in. 🧘‍♀️\n1. How are your energy levels?\n2. Any soreness?\n3. Have you moved your body today?"
        
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e:
        print(f"Failed to trigger body check: {e}")

async def trigger_breakfast_reminder():
    """Trigger breakfast reminder at 9:30 AM."""
    if not USER_TELEGRAM_ID or not application:
        return
        
    print("Triggering Breakfast Reminder...")
    try:
        if not application._initialized:
            await application.initialize()
            
        msg = "Time for breakfast! 🍳 What are you having? Feel free to share a photo so I can check the nutrition balance."
        
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e:
        print(f"Failed to trigger breakfast reminder: {e}")

async def trigger_lunch_reminder():
    """Trigger lunch reminder at 12:30 PM."""
    if not USER_TELEGRAM_ID or not application:
        return
        
    print("Triggering Lunch Reminder...")
    try:
        if not application._initialized:
            await application.initialize()
            
        msg = "Lunch time! 🥗 What's on your plate today? Send me a pic and I'll give you feedback on the macros."
        
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e:
        print(f"Failed to trigger lunch reminder: {e}")

async def trigger_dinner_reminder():
    """Trigger dinner reminder at 6:00 PM."""
    if not USER_TELEGRAM_ID or not application:
        return
        
    print("Triggering Dinner Reminder...")
    try:
        if not application._initialized:
            await application.initialize()
            
        msg = "Dinner time! 🍽️ Let's see what you're fueling your body with tonight. Share a photo for my analysis!"
        
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e:
        print(f"Failed to trigger dinner reminder: {e}")

async def trigger_stretch_reminder():
    """Trigger stretch/break reminder."""
    if not USER_TELEGRAM_ID or not application:
        return
        
    print("Triggering Stretch Reminder...")
    try:
        if not application._initialized:
            await application.initialize()
            
        msg = "Time to move! 🧘‍♀️ You've been sitting for a while. Take 5 minutes to:\n• Stand up and stretch\n• Roll your shoulders\n• Walk around\n• Hydrate 💧\n\nYour body will thank you!"
        
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e:
        print(f"Failed to trigger stretch reminder: {e}")

async def trigger_evening_winddown():
    """Trigger evening wind-down routine at 10:25 PM."""
    if not USER_TELEGRAM_ID or not application:
        return
        
    print("Triggering Evening Wind-Down...")
    try:
        if not application._initialized:
            await application.initialize()
            
        msg = """Time to wind down for the night! 🌙

Let's recap today:
• What did you eat today? Any meals you're proud of?
• Did you get your movement/exercise in?

**Sleep prep tips:**
✨ Try 5 deep breaths (4-7-8 technique)
📱 Put your phone away in 10 minutes
🙏 Think of one thing you're grateful for today

Get ready for bed soon - quality sleep is the foundation of everything! 😴💤"""
        
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e:
        print(f"Failed to trigger evening wind-down: {e}")

if __name__ == "__main__":
    asyncio.run(proactive_loop())
