import logging

from backoffice.celery import app as celery_app
from ddd.logic.application.commands import SendAttributionEndDateReachedSummaryCommand
from django.conf import settings
from infrastructure.messages_bus import message_bus_instance

logger = logging.getLogger(settings.DEFAULT_LOGGER)


@celery_app.task
def run() -> dict:
    logger.info("Task send_attribution_end_date_reached_summary started")
    cmd = SendAttributionEndDateReachedSummaryCommand()
    message_bus_instance.invoke(cmd)
    return {}
