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
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from base import models as mdl
from ddd.logic.encodage_des_notes.encodage.commands import GetPeriodeEncodageCommand
from infrastructure.messages_bus import message_bus_instance
from osis_role.contrib.views import PermissionRequiredMixin

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


class OutsidePeriod(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "assessments/outside_scores_encodings_period.html"
    permission_required = 'assessments.can_access_scoreencoding'
    raise_exception = True
    login_url = reverse_lazy('assessments')
    date_format = str(_('date_format'))

    def test_func(self):
        return not self._is_inside_scores_encodings_period()

    @staticmethod
    def _is_inside_scores_encodings_period() -> bool:
        return bool(message_bus_instance.invoke(GetPeriodeEncodageCommand()))

    def get_context_data(self, **kwargs):
        messages_str = get_latest_closest_session_information_message()

        for message in messages_str:
            messages.add_message(
                self.request,
                messages.WARNING,
                message
            )

        if not messages.get_messages(self.request):
            messages.add_message(self.request, messages.WARNING, _("The period of scores' encoding is not opened"))

        return {
            **super().get_context_data(**kwargs)
        }


def get_latest_closest_session_information_message():
    messages_str = []
    date_format = str(_('date_format'))
    latest_session_exam = mdl.session_exam_calendar.get_latest_session_exam()
    closest_new_session_exam = mdl.session_exam_calendar.get_closest_new_session_exam()
    if latest_session_exam:
        month_session = latest_session_exam.month_session_name()
        str_date = latest_session_exam.end_date.strftime(date_format)
        messages_str.append(
            _("The period of scores' encoding for %(month_session)s session is closed since %(str_date)s")
            % {'month_session': month_session, 'str_date': str_date})
    if closest_new_session_exam:
        month_session = closest_new_session_exam.month_session_name()
        str_date = closest_new_session_exam.start_date.strftime(date_format)
        messages_str.append(
            _("The period of scores' encoding for %(month_session)s session will be open %(str_date)s")
            % {'month_session': month_session, 'str_date': str_date})
    return messages_str
