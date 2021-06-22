##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import json
import logging

from django.conf import settings

from ddd.logic.application.domain.model.application import Application
from infrastructure.application.serializer.application import ApplicationSerializer
from osis_common.queue import queue_sender

queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


def notify_application_deleted(application: Application):
    queue_name = settings.QUEUES.get('QUEUES_NAME', {}).get('APPLICATION_REQUEST')
    if queue_name:
        message_serialized = ApplicationSerializer().serialize_to_delete_epc_message(application)
        queue_sender.send_message(queue_name, message_serialized)
        log_msg = "Application deleted message sent: {}".format(json.dumps(message_serialized))
        queue_exception_logger.info(log_msg)


def notify_application_saved(application: Application):
    queue_name = settings.QUEUES.get('QUEUES_NAME', {}).get('APPLICATION_REQUEST')
    if queue_name:
        message_serialized = ApplicationSerializer().serialize_to_update_epc_message(application)
        queue_sender.send_message(queue_name, message_serialized)
        log_msg = "Application save message sent: {}".format(json.dumps(message_serialized))
        queue_exception_logger.info(log_msg)


def application_response_callback(message_payload: any):
    """
        Callback of APPLICATION_RESPONSE queue
    """
    json_data = message_payload.decode("utf-8")
    application = json.loads(json_data)

    error_epc = application.get("error")
    if error_epc:
        log_msg = 'Error during processing tutor application in EPC: {} \n JSON: {}'.format(error_epc, str(json_data))
        queue_exception_logger.error(log_msg)
        raise Exception(log_msg)
