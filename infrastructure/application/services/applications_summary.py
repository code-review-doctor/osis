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
from typing import List

from django.utils.translation import pgettext_lazy

from base.models.person import Person
from ddd.logic.application.domain.model.applicant import Applicant
from ddd.logic.application.domain.model.application import Application
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar
from ddd.logic.application.domain.service.applications_summary import ApplicationsSummary
from osis_common.messaging import message_config, send_message as message_service


class ApplicationsMailSummary(ApplicationsSummary):

    @classmethod
    def send(cls, applicant: Applicant, application_calendar: ApplicationCalendar, applications: List[Application]):
        html_template_ref = 'applications_confirmation_html'
        txt_template_ref = 'applications_confirmation_txt'

        person = Person.objects.get(global_id=applicant.entity_id.global_id)
        receivers = [
            message_config.create_receiver(person.id, person.email, person.language)
        ]

        table_applications = message_config.create_table(
            'applications',
            [pgettext_lazy("applications", "Code"), 'Vol. 1', 'Vol. 2'],
            [
                (application.vacant_course_id.code, application.lecturing_volume, application.practical_volume,)
                for application in applications
            ]
        )
        template_base_data = {
            'first_name': applicant.first_name,
            'last_name': applicant.last_name,
            'application_courses_targeted_year': application_calendar.authorized_target_year
        }
        message_content = message_config.create_message_content(
            html_template_ref, txt_template_ref, [table_applications], receivers, template_base_data, None
        )
        message_service.send_messages(message_content)
