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

from django import forms
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from rules.contrib.views import LoginRequiredMixin

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.utils.htmx import HtmxMixin
from base.views.common import display_error_messages, display_success_messages
from ddd.logic.learning_unit.commands import LearningUnitSearchCommand
from ddd.logic.learning_unit.dtos import LearningUnitSearchDTO
from ddd.logic.preparation_programme_annuel_etudiant.commands import AjouterUEAuProgrammeCommand
from ddd.logic.shared_kernel.academic_year.commands import SearchAcademicYearCommand
from education_group.forms.fields import UpperCaseCharField
from infrastructure.messages_bus import message_bus_instance
from preparation_inscription.views.consulter_contenu_groupement import ConsulterContenuGroupementView


class SearchLearningUnitForm(forms.Form):
    annee_academique = forms.ChoiceField(
        label=_("Anac.").capitalize(),
        required=False
    )
    code = UpperCaseCharField(max_length=15, label=_("Code").capitalize(), required=False)
    intitule = forms.CharField(max_length=30, label=_("Title").capitalize(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_academic_year_field()

    def __init_academic_year_field(self):
        all_academic_year = message_bus_instance.invoke(
            SearchAcademicYearCommand()
        )
        self.fields['annee_academique'].choices = [(ac_year.year, str(ac_year)) for ac_year in all_academic_year]


class AjouterUnitesEnseignementView(LoginRequiredMixin, HtmxMixin, TemplateView):
    name = 'ajouter_unites_enseignement_view'

    # FormView
    template_name = "preparation_inscription/preparation_inscription.html"
    htmx_template_name = "preparation_inscription/ajouter_unites_enseignement.html"

    def get_search_form(self):
        return SearchLearningUnitForm(
            data=self.request.GET or None,
            initial={
                'annee_academique': 2021
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
            annee_formation=2021,
            sigle_formation='ECGE1BA',
            version_formation='',
            transition_formation='',
            ajouter_dans='LECGE100R',
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

        return redirect("consulter_contenu_groupement_view")

    def get_intitule_groupement(self):
        # TODO :: to implement
        return "Intitulé groupement"

    def get_intitule_programme(self):
        # TODO :: to implement
        return "Intitulé programme"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'search_form': self.get_search_form(),
            'search_result': self.get_search_result(),
            'intitule_groupement': self.get_intitule_groupement(),
            'intitule_programme': self.get_intitule_programme(),
            'cancel_url': reverse(ConsulterContenuGroupementView.name)
        }
