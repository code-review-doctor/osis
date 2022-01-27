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
import datetime
import logging

from django.conf import settings
from django.utils.translation import pgettext_lazy

from base.business.education_group import DATE_FORMAT
from base.models.person import Person
from ddd.logic.application.commands import GetAttributionsAboutToExpireCommand
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar
from ddd.logic.application.domain.service.attributions_end_date_reached_summary import \
    IAttributionsEndDateReachedSummary
from ddd.logic.application.repository.i_applicant_respository import IApplicantRepository
from osis_common.messaging import message_config, send_message as message_service
from osis_common.models.message_history import MessageHistory

logger = logging.getLogger(settings.DEFAULT_LOGGER)

HTML_TEMPLATE_REF = 'ending_attributions_html'
TXT_TEMPLATE_REF = 'ending_attributions_txt'


class AttributionsEndDateReachedSummary(IAttributionsEndDateReachedSummary):

    @classmethod
    def send(
            cls,
            application_calendar: ApplicationCalendar,
            applicant_repository: IApplicantRepository
    ):
        from infrastructure.messages_bus import message_bus_instance

        today_date = datetime.date.today()
        if application_calendar.start_date == today_date:
            applicants = applicant_repository.search()

            for applicant in applicants:
                person = Person.objects.filter(global_id=applicant.entity_id.global_id).first()

                if person.email and not mail_already_sent(today=today_date, receiver_email=person.email):
                    try:
                        cmd = GetAttributionsAboutToExpireCommand(global_id=applicant.entity_id.global_id)
                        attributions_about_to_expire = message_bus_instance.invoke(cmd)
                    except Exception as e:
                        logger.info(
                            "[AttributionEndDateReachedSummary - {}] An error occured during retrieval attributions "
                            "about to expire for {} : {}".format(today_date, person.email, str(e))
                        )
                        continue

                    if attributions_about_to_expire:
                        receivers = [message_config.create_receiver(person.id, person.email, person.language)]
                        table_ending_attributions = message_config.create_table(
                            'ending_attributions',
                            [pgettext_lazy("applications", "Code"), 'Title', 'Vol. 1', 'Vol. 2'],
                            [
                                (
                                    attributions_ending.code,
                                    attributions_ending.title,
                                    attributions_ending.lecturing_volume,
                                    attributions_ending.practical_volume,
                                )
                                for attributions_ending in attributions_about_to_expire
                            ]
                        )
                        template_base_data = {
                            'first_name': person.first_name,
                            'last_name': person.last_name,
                            'end_date': application_calendar.end_date.strftime(DATE_FORMAT)
                        }
                        message_content = message_config.create_message_content(
                            HTML_TEMPLATE_REF,
                            TXT_TEMPLATE_REF,
                            [table_ending_attributions],
                            receivers,
                            template_base_data,
                            None
                        )
                        message_service.send_messages(message_content)
                        logger.info(
                            "[AttributionEndDateReachedSummary - {}] Mail sent to {}".format(today_date, person.email)
                        )
                    else:
                        logger.info(
                            "[AttributionEndDateReachedSummary - {}] No attributions about to expire for {}".format(
                                today_date, person.email
                            )
                        )
        else:
            logger.info(
                "[AttributionEndDateReachedSummary - {}] Application course start date not reached".format(today_date)
            )


def mail_already_sent(today, receiver_email: str) -> bool:
    # FIXME: fix reference on send method of message_service in order to prevent use subject...
    mail_already_sent_today = MessageHistory.objects.filter(
        subject="Charges d'enseignement de vos cours arrivant à échéance",
        sent__date=today,
        receiver_email=receiver_email
    ).exists()
    if mail_already_sent_today:
        logger.info("[AttributionEndDateReachedSummary - {}] Mail already sent to {}".format(today, receiver_email))
    return mail_already_sent_today
