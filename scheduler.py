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

db = DatabaseService()

async def proactive_loop():
    """Main scheduler loop."""
    print("Elena Scheduler started.")
    
    # State to prevent double sending in the same minute
    last_sent_date = None
    
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        
        # Get current EST time
        est_offset = timezone(timedelta(hours=-5))
        now = datetime.now(est_offset)
        current_date_str = now.strftime("%Y-%m-%d")
        
        # 9:00 AM Check-in
        if now.hour == 9 and now.minute == 0:
            if last_sent_date != current_date_str:
                await trigger_daily_checkin()
                
                # Check for 3-day body check
                # Simple logic: if day of year is divisible by 3
                day_of_year = now.timetuple().tm_yday
                if day_of_year % 3 == 0:
                    await trigger_body_check()
                
                last_sent_date = current_date_str

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

if __name__ == "__main__":
    asyncio.run(proactive_loop())
