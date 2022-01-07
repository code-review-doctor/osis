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
from typing import Any

from django.conf import settings

from attribution.models.tutor_application import TutorApplication
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
    else:
        log_msg = "[APPLICATION] Settings APPLICATION_REQUEST (QUEUES) missing"
        queue_exception_logger.info(log_msg)


def notify_application_saved(application: Application):
    queue_name = settings.QUEUES.get('QUEUES_NAME', {}).get('APPLICATION_REQUEST')
    if queue_name:
        message_serialized = ApplicationSerializer().serialize_to_update_epc_message(application)
        queue_sender.send_message(queue_name, message_serialized)
        log_msg = "Application save message sent: {}".format(json.dumps(message_serialized))
        queue_exception_logger.info(log_msg)
    else:
        log_msg = "[APPLICATION] Settings APPLICATION_REQUEST (QUEUES) missing"
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

    operation = application.get('operation')
    global_id = application.get('global_id')
    acronym = application.get('learning_container_year', {}).get('acronym')
    year = application.get('learning_container_year', {}).get('year')
    num_ele_itv = application.get('num_ele_itv')
    if not (global_id and acronym and year and operation and num_ele_itv):
        log_msg = 'Missing mandatory data in tutor application response from EPC. JSON: {}'.format(str(json_data))
        queue_exception_logger.error(log_msg)
        raise Exception(log_msg)

    if operation == "update":
        __update_tutor_application(global_id, acronym, year, num_ele_itv)
    if operation == "delete":
        __delete_tutor_application(num_ele_itv)


def __update_tutor_application(global_id: str, acronym: str, year: Any, num_ele_itv: str):
    external_id_computed = 'osis.tutor_application_{num_ele_itv}'.format(num_ele_itv=num_ele_itv)
    existing_application = TutorApplication.objects.get(
        learning_container_year__academic_year__year=int(year),
        learning_container_year__acronym=acronym,
        tutor__person__global_id=global_id
    )
    if existing_application.external_id == external_id_computed:
        return
    if existing_application.external_id and existing_application.external_id != external_id_computed:
        log_msg = """
               Multiple external_id for same tutor application [global_id: {global_id} / course: {acronym}-{year}]
               current: {current_external_id} / new: {external_id_computed}
           """.format(
            global_id=global_id,
            acronym=acronym,
            year=str(year),
            current_external_id=existing_application.external_id,
            external_id_computed=external_id_computed
        )
        queue_exception_logger.error(log_msg)
        raise Exception(log_msg)

    existing_application.external_id = external_id_computed
    existing_application.save()
    log_msg = "Tutor Application [global_id: {global_id} / course: {acronym}-{year}] external_id updated".format(
        global_id=global_id,
        acronym=acronym,
        year=str(year),
    )
    queue_exception_logger.info(log_msg)


def __delete_tutor_application(num_ele_itv: str):
    external_id_computed = 'osis.tutor_application_{num_ele_itv}'.format(num_ele_itv=num_ele_itv)
    TutorApplication.objects.filter(external_id=external_id_computed).delete()
    log_msg = "Tutor Application [external_id: {}] deleted".format(external_id_computed)
    queue_exception_logger.info(log_msg)
