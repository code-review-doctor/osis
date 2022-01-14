from backoffice.celery import app as celery_app
from ddd.logic.application.commands import SendAttributionEndDateReachedSummaryCommand
from infrastructure.messages_bus import message_bus_instance


@celery_app.task
def run() -> dict:
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #  To be executed once a day
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    cmd = SendAttributionEndDateReachedSummaryCommand()
    message_bus_instance.invoke(cmd)
    return {}
