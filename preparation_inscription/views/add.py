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

from django import forms
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from rules.contrib.views import LoginRequiredMixin

from base.utils.htmx import HtmxMixin
from ddd.logic.shared_kernel.academic_year.commands import SearchAcademicYearCommand
from education_group.forms.fields import UpperCaseCharField
from infrastructure.messages_bus import message_bus_instance


class SearchLearningUnitForm(forms.Form):
    annee_academique = forms.ChoiceField(
        label=_("Academic year").capitalize(),
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


class AddLearningUnitFormView(LoginRequiredMixin, HtmxMixin, TemplateView):
    name = 'add-learning-unit'

    # FormView
    template_name = "preparation_inscription/add.html"
    htmx_template_name = "preparation_inscription/html_add.html"

    def get_search_form(self):
        return SearchLearningUnitForm(
            data=self.request.GET or None,
            initial={
                'annee_academique': 2021
            }
        )

    def get_search_result(self):
        data = [
            {
                'annee_academique': '2021',
                'code': 'LSINF1452',
                'intitule': 'Test en EPC',
            },
            {
                'annee_academique': '2021',
                'code': 'LECGE12547',
                'intitule': 'Finance en Osis',
            },
        ]  # TODO :: message_bus.invoke(Command)
        return data

    def post(self, request, *args, **kwargs):
        selected_ues = request.POST.getlist('selected_ue')
        # TODO :: to implement
        # cmd = Command(...)
        # message__bus.invoke(cmd)
        # display_error_messages(self.request, messages)
        # display_success_messages(self.request, messages)
        # self.render_to_response(self.get_context_data(form=self.get_form(self.form_class)))
        return redirect("detail-program")

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'search_form': self.get_search_form(),
            'search_result': self.get_search_result(),
            'intitule_groupement': "MAT1ECGE - Formation pluridisciplinaires en sciences humaines",
            'intitule_programme': 'ECGE1BA - 2021-2022',
            'cancel_url': reverse('detail-program')
        }
