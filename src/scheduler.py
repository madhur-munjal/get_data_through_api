# from apscheduler.schedulers.background import BackgroundScheduler
# from fastapi import FastAPI
#
# from src.utility import update_appointment_status
#
# app = FastAPI()
# scheduler = BackgroundScheduler()
# scheduler.add_job(update_appointment_status, 'cron', hour=23, minute=45)
# scheduler.start()
#
# # from apscheduler.triggers.cron import CronTrigger
# # trigger = CronTrigger(hour=23, minute=30)
# # scheduler.add_job(update_appointment_status, trigger=trigger, name="Daily Status Update")
# # scheduler.start()
#

from apscheduler.schedulers.background import BackgroundScheduler

from src.utility import update_appointment_status, update_subscription_data

scheduler = BackgroundScheduler()


def start_scheduler():
    """Initialize and start the scheduler"""
    scheduler.add_job(update_appointment_status, 'cron', hour=23, minute=45)
    scheduler.add_job(update_subscription_data, 'cron', hour=00, minute=1)
    scheduler.start()
    print("Scheduler's started - Will run update_appointment_status daily at 23:45 and update_subscription_data at 00:00")


def shutdown_scheduler():
    """Shutdown the scheduler gracefully"""
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler shut down")
