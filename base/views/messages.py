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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.messages import get_messages, INFO, SUCCESS, ERROR, WARNING
from django.views.generic import TemplateView
from rules.contrib.views import LoginRequiredMixin

from base.utils.htmx import HtmxMixin


class GetMessagesView(LoginRequiredMixin, HtmxMixin, TemplateView):
    name = "get_messages"
    template_name = "base/messages.html"
    htmx_template_name = "base/messages.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        storage = get_messages(self.request)

        success_messages = []
        info_messages = []
        warning_messages = []
        error_messages = []

        for message in storage:
            if message.level == SUCCESS:
                success_messages.append(message)
            elif message.level == INFO:
                info_messages.append(message)
            elif message.level == WARNING:
                warning_messages.append(message)
            elif message.level == ERROR:
                error_messages.append(message)

        context.update({
            "success": success_messages,
            "info": info_messages,
            "warning": warning_messages,
            "error": error_messages
        })

        return context

