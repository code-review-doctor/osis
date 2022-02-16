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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.views.common import display_success_messages, display_error_messages
from base.views.mixins import AjaxTemplateMixin
from ddd.logic.preparation_programme_annuel_etudiant.commands import RemettreProgrammeDansEtatInitialCommand
from infrastructure.messages_bus import message_bus_instance
from osis_role.contrib.views import PermissionRequiredMixin


class RemettreEtatInitialView(LoginRequiredMixin, PermissionRequiredMixin, AjaxTemplateMixin, FormView):
    name = 'remettre_etat_initial_view'
    template_name = "preparation_inscription/modal_confirmer_remettre_etat_initial_inner.html"
    form_class = Form
    permission_required = 'preparation_programme.can_reinit_programme_inscription'

    @property
    def annee(self):
        return self.kwargs['annee']

    @property
    def code_programme(self):
        return self.kwargs['code_programme']

    def post(self, request, *args, **kwargs):
        try:
            command = RemettreProgrammeDansEtatInitialCommand(
                code_programme=self.code_programme,
                annee=self.annee
            )
            message_bus_instance.invoke(command)
            display_success_messages(request, _("The program has returned to its original state."))
            return super().post(*args, **kwargs)
        except MultipleBusinessExceptions as exceptions:
            messages = [exception.message for exception in exceptions.exceptions]
            display_error_messages(request, messages)
            return self.get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('preparation-inscription-main-view', kwargs={
            'code_programme': self.code_programme,
            'annee': self.annee
        })
