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
from typing import List

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from rules.contrib.views import LoginRequiredMixin

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.utils.htmx import HtmxMixin
from base.views.common import display_error_messages, display_success_messages
from ddd.logic.learning_unit.commands import LearningUnitSearchCommand
from ddd.logic.learning_unit.dtos import LearningUnitSearchDTO
from ddd.logic.preparation_programme_annuel_etudiant.commands import AjouterUEAuProgrammeCommand
from infrastructure.messages_bus import message_bus_instance
from preparation_inscription.forms.search_learning_units import SearchLearningUnitForm
from preparation_inscription.views.consulter_contenu_groupement import RAFRAICHIR_GROUPEMENT_CONTENANT


class AjouterUnitesEnseignementView(LoginRequiredMixin, HtmxMixin, TemplateView):
    name = 'ajouter_unites_enseignement_view'

    template_name = "preparation_inscription/ajouter_unites_enseignement.html"
    htmx_template_name = "preparation_inscription/ajouter_unites_enseignement.html"

    @cached_property
    def code_programme(self):
        return self.kwargs['code_programme']

    @cached_property
    def code_groupement(self):
        return self.kwargs['code_groupement']

    @cached_property
    def annee(self):
        return self.kwargs['annee']

    def get_search_form(self):
        return SearchLearningUnitForm(
            data=self.request.GET or None,
            initial={
                'annee_academique': self.annee
            }
        )

    def get_search_result(self) -> List['LearningUnitSearchDTO']:
        search_form = self.get_search_form()
        if search_form.is_valid():

            cmd = LearningUnitSearchCommand(
                code_annee_values=None,
                code=search_form.cleaned_data['code'],
                annee_academique=int(search_form.cleaned_data['annee_academique']),
                intitule=search_form.cleaned_data['intitule'],
            )
            return message_bus_instance.invoke(cmd)

        return []

    def post(self, request, *args, **kwargs):
        selected_ues = request.POST.getlist('selected_ue')
        cmd = AjouterUEAuProgrammeCommand(
            annee=self.annee,
            code_programme=self.code_programme,
            ajouter_dans=self.code_groupement,
            unites_enseignements=selected_ues
        )
        try:
            message_bus_instance.invoke(cmd)
            success_message = _('The learning units have been added')
            display_success_messages(self.request, success_message)
        except MultipleBusinessExceptions as exceptions:
            messages = [exception.message for exception in exceptions.exceptions]
            display_error_messages(self.request, messages)
            return self.get(request, *args, **kwargs)
        return redirect(self.get_consulter_contenu_groupement_url())

    def get_intitule_groupement(self):
        return self.code_groupement

    def get_intitule_programme(self):
        return self.code_programme

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'search_form': self.get_search_form(),
            'search_result': self.get_search_result(),
            'intitule_groupement': self.get_intitule_groupement(),
            'intitule_programme': self.get_intitule_programme(),
            'cancel_url': self.get_consulter_contenu_groupement_url(),
            'annee': self.annee,
            'code_programme': self.code_programme,
            'code_groupement': self.code_groupement
        }

    def get_consulter_contenu_groupement_url(self):
        return reverse(
            'consulter_contenu_groupement_view',
            kwargs={
                "annee": self.annee,
                "code_programme": self.code_programme,
                "code_groupement": self.code_groupement
            }
        ) + "?{}=1".format(RAFRAICHIR_GROUPEMENT_CONTENANT)
