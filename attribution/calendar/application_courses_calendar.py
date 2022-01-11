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
import datetime

from django.utils.translation import pgettext_lazy

from attribution.models.attribution_new import AttributionNew
from base.business.academic_calendar import AcademicEventCalendarHelper
from base.business.education_group import DATE_FORMAT
from base.models.academic_calendar import AcademicCalendar
from base.models.academic_year import AcademicYear
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from ddd.logic.application.commands import GetAttributionsAboutToExpireCommand
from osis_common.messaging import message_config, send_message as message_service


class ApplicationCoursesCalendar(AcademicEventCalendarHelper):
    event_reference = AcademicCalendarTypes.TEACHING_CHARGE_APPLICATION.name

    @classmethod
    def ensure_consistency_until_n_plus_6(cls):
        current_academic_year = AcademicYear.objects.current()
        academic_years = AcademicYear.objects.min_max_years(current_academic_year.year, current_academic_year.year + 6)

        for ac_year in academic_years:
            AcademicCalendar.objects.get_or_create(
                reference=cls.event_reference,
                data_year=ac_year,
                defaults={
                    "title": "Candidature aux cours vacants",
                    "start_date": datetime.date(ac_year.year, 2, 1),
                    "end_date": datetime.date(ac_year.year, 2, 14),
                }
            )

    @classmethod
    def send_emails_to_teachers_with_ending_attributions(cls):
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #  To be executed once a day
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        today = datetime.date.today()

        current_academic_year = AcademicYear.objects.current()
        next_year = AcademicYear.objects.get(year=current_academic_year.year+1)

        opened_calendar = AcademicCalendar.objects.filter(
            reference=cls.event_reference,
            data_year=next_year,
            start_date=today).first()

        if opened_calendar:
            html_template_ref = 'ending_attributions_html'
            txt_template_ref = 'ending_attributions_txt'
            attributions = AttributionNew.objects.filter(
                learning_container_year__academic_year=current_academic_year
            ).distinct('tutor__person')

            for attribution in attributions:
                person = attribution.tutor.person
                global_id = attribution.tutor.person.global_id
                cmd = GetAttributionsAboutToExpireCommand(global_id=global_id)
                from infrastructure.messages_bus import message_bus_instance
                attributions_ending = message_bus_instance.invoke(cmd)
                if len(attributions_ending) > 0:
                    receivers = [message_config.create_receiver(person.id, person.email, person.language)]
                    table_applications = message_config.create_table(
                        'ending_attributions',
                        [pgettext_lazy("applications", "Code"), 'Vol. 1', 'Vol. 2'],
                        [
                            (
                                attributions_ending.code,
                                attributions_ending.lecturing_volume,
                                attributions_ending.practical_volume,
                            )
                            for attributions_ending in attributions_ending
                        ]
                    )
                    template_base_data = {'first_name': person.first_name,
                                          'last_name': person.last_name,
                                          'end_date': opened_calendar.end_date.strftime(DATE_FORMAT)
                                          }
                    message_content = message_config.create_message_content(
                        html_template_ref,
                        txt_template_ref,
                        [table_applications],
                        receivers,
                        template_base_data
                    )
                    message_service.send_messages(message_content)
