import asyncio
import os
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # Fallback for older Python versions

from services.telegram_bot import application
from services.database import DatabaseService
from dotenv import load_dotenv

load_dotenv()

# Configuration
CHECK_INTERVAL = 60 # Check every minute
USER_TELEGRAM_ID = os.getenv("USER_TELEGRAM_ID") 

# Define Timezone
NYC_TZ = ZoneInfo("America/New_York")

db = DatabaseService()

async def proactive_loop():
    """Main scheduler loop."""
    print(f"Elena Scheduler started. Timezone: {NYC_TZ}")
    
    # State to prevent double sending
    last_sent_minute = None
    
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        
        # Get current NYC time
        now = datetime.now(NYC_TZ)
        current_minute_key = f"{now.day}-{now.hour}:{now.minute}"
        
        # Prevent double triggering if loop runs fast
        if last_sent_minute == current_minute_key:
            continue
            
        last_sent_minute = current_minute_key
        
        # --- FIXED SCHEDULE EVENTS ---
        
        # 9:00 AM Daily Check-in
        if now.hour == 9 and now.minute == 0:
            await trigger_daily_checkin()
            
            # Check for 3-day body check (Day of year % 3)
            day_of_year = now.timetuple().tm_yday
            if day_of_year % 3 == 0:
                await trigger_body_check()
        
        # 9:30 AM Breakfast
        if now.hour == 9 and now.minute == 30:
            await trigger_breakfast_reminder()
        
        # 12:30 PM Lunch
        if now.hour == 12 and now.minute == 30:
            await trigger_lunch_reminder()
        
        # 6:00 PM Dinner
        if now.hour == 18 and now.minute == 0:
            await trigger_dinner_reminder()
        
        # 10:25 PM Evening Wind-Down
        if now.hour == 22 and now.minute == 25:
            await trigger_evening_winddown()
            
        # --- STRETCH REMINDERS (Fixed Slots) ---
        # Schedule: 10:00, 11:30, 13:00, 14:30, 16:00, 17:30, 19:00, 20:30, 22:00, 23:30
        stretch_slots = [
            (10, 0), (11, 30),
            (13, 0), (14, 30),
            (16, 0), (17, 30),
            (19, 0), (20, 30),
            (22, 0), (23, 30)
        ]
        
        if (now.hour, now.minute) in stretch_slots:
            await trigger_stretch_reminder()

async def trigger_daily_checkin():
    """Trigger daily sleep/diet check."""
    if not USER_TELEGRAM_ID or not application:
        return
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
    try:
        if not application._initialized:
            await application.initialize()
        msg = "Time for a body check-in. 🧘‍♀️\n1. How are your energy levels?\n2. Any soreness?\n3. Have you moved your body today?"
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e:
        print(f"Failed to trigger body check: {e}")

async def trigger_breakfast_reminder():
    if not USER_TELEGRAM_ID or not application: return
    try:
        if not application._initialized: await application.initialize()
        msg = "Time for breakfast! 🍳 What are you having? Feel free to share a photo so I can check the nutrition balance."
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e: print(f"Failed to trigger breakfast reminder: {e}")

async def trigger_lunch_reminder():
    if not USER_TELEGRAM_ID or not application: return
    try:
        if not application._initialized: await application.initialize()
        msg = "Lunch time! 🥗 What's on your plate today? Send me a pic and I'll give you feedback on the macros."
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e: print(f"Failed to trigger lunch reminder: {e}")

async def trigger_dinner_reminder():
    if not USER_TELEGRAM_ID or not application: return
    try:
        if not application._initialized: await application.initialize()
        msg = "Dinner time! 🍽️ Let's see what you're fueling your body with tonight. Share a photo for my analysis!"
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e: print(f"Failed to trigger dinner reminder: {e}")

async def trigger_stretch_reminder():
    if not USER_TELEGRAM_ID or not application: return
    print("Triggering Stretch Reminder...")
    try:
        if not application._initialized: await application.initialize()
        msg = "Time to move! 🧘‍♀️ You've been sitting for a while. Take 5 minutes to:\n• Stand up and stretch\n• Roll your shoulders\n• Walk around\n• Hydrate 💧\n\nYour body will thank you!"
        await application.bot.send_message(chat_id=USER_TELEGRAM_ID, text=msg)
        await db.save_message(USER_TELEGRAM_ID, "assistant", msg, "telegram_elena")
    except Exception as e: print(f"Failed to trigger stretch reminder: {e}")

async def trigger_evening_winddown():
    if not USER_TELEGRAM_ID or not application: return
    print("Triggering Evening Wind-Down...")
    try:
        if not application._initialized: await application.initialize()
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
    except Exception as e: print(f"Failed to trigger evening wind-down: {e}")

if __name__ == "__main__":
    asyncio.run(proactive_loop())
