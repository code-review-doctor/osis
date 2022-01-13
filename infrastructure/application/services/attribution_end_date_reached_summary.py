##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import logging
from typing import List

from django.conf import settings
from django.utils.translation import pgettext_lazy

from base.business.education_group import DATE_FORMAT
from base.models.person import Person
from ddd.logic.application.domain.model._attribution import Attribution
from ddd.logic.application.domain.model.applicant import Applicant
from ddd.logic.application.domain.service.attributions_end_date_reached_summary import \
    IAttributionsEndDateReachedSummary
from osis_common.messaging import message_config, send_message as message_service

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class AttributionsEndDateReachedSummary(IAttributionsEndDateReachedSummary):

    @classmethod
    def send(
            cls,
            applicant: Applicant,
            attributions_ending: List[Attribution],
            end_date: str
    ):

        html_template_ref = 'ending_attributions_html'
        txt_template_ref = 'ending_attributions_txt'

        person = Person.objects.get(global_id=applicant.entity_id.global_id)
        receivers = [message_config.create_receiver(person.id, person.email, person.language)]
        table_ending_attributions = message_config.create_table(
            'ending_attributions',
            [pgettext_lazy("applications", "Code"), 'Vol. 1', 'Vol. 2'],
            [
                (
                    attributions_ending.course_id.code,
                    attributions_ending.lecturing_volume,
                    attributions_ending.practical_volume,
                )
                for attributions_ending in attributions_ending
            ]
        )
        template_base_data = {
            'first_name': person.first_name,
            'last_name': person.last_name,
            'end_date': end_date.strftime(DATE_FORMAT)
        }
        message_content = message_config.create_message_content(
            html_template_ref,
            txt_template_ref,
            [table_ending_attributions],
            receivers,
            template_base_data,
            None
        )
        message_service.send_messages(message_content)
