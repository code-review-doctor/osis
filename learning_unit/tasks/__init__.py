from . import check_academic_calendar

from celery.schedules import crontab
from backoffice.celery import app as celery_app
celery_app.conf.beat_schedule.update({
    '|Learning unit| Check academic calendar': {
        'task': 'learning_unit.tasks.check_academic_calendar.run',
        'schedule': crontab(minute=0, hour=0, day_of_month='*', month_of_year='*', day_of_week=0)
    },
})


celery_app.conf.beat_schedule.update({
    '|Learning Unit| General postponement of learning unit until n+6': {
        'task': 'learning_unit.tasks.postpone_learning_units_until_n_plus_6.run',
        'schedule': crontab(minute=0, hour=0, day_of_month='2', month_of_year='7', day_of_week=0)
    },
})
