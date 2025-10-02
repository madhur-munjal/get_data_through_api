from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from src.utility import update_appointment_status

app = FastAPI()
scheduler = BackgroundScheduler()
scheduler.add_job(update_appointment_status, 'cron', hour=23, minute=45)
scheduler.start()

# from apscheduler.triggers.cron import CronTrigger
# trigger = CronTrigger(hour=23, minute=30)
# scheduler.add_job(update_appointment_status, trigger=trigger, name="Daily Status Update")
# scheduler.start()
