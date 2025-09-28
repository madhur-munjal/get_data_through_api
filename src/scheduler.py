from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from src.utility import update_appointment_status

app = FastAPI()
scheduler = BackgroundScheduler()
scheduler.add_job(update_appointment_status, 'cron', hour=23, minute=45)
scheduler.start()