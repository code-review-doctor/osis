from . import check_academic_calendar
from . import send_attribution_end_date_reached_summary

from celery.schedules import crontab
from backoffice.celery import app as celery_app
celery_app.conf.beat_schedule.update({
    '|Attribution| Check academic calendar': {
        'task': 'attribution.tasks.check_academic_calendar.run',
        'schedule': crontab(minute=0, hour=0, day_of_month='*', month_of_year='*', day_of_week=0)
    },
    '|Attribution| Send attributions about to expired': {
        'task': 'attribution.tasks.send_attribution_end_date_reached_summary.run',
        'schedule': crontab(minute=0, hour=16, day_of_month='*', month_of_year='*', day_of_week=0)
    },
})
