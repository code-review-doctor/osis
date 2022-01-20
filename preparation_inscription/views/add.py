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
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from rules.contrib.views import LoginRequiredMixin

from base.forms.utils.choice_field import add_blank
from base.models.enums.active_status import ActiveStatusEnum
from education_group.forms.fields import UpperCaseCharField


class SearchLearningUnitForm(forms.Form):
    annee_academique = forms.ChoiceField(
        initial=ActiveStatusEnum.ACTIVE.name,
        choices=add_blank(list(ActiveStatusEnum.choices())),
        label=_("Academic year").capitalize(),
        required=False
    )
    code = UpperCaseCharField(max_length=15, label=_("Code").capitalize(), required=False)
    intitule = forms.CharField(max_length=30, label=_("Title").capitalize(), required=False)

    def __init__(self, *args, user: User, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)


class AddLearningUnitFormView(LoginRequiredMixin, FormView):
    name = 'add-learning-unit'

    # FormView
    template_name = "preparation_inscription/add.html"

    form_class = SearchLearningUnitForm

    def get_search_form(self):
        return SearchLearningUnitForm(data=self.request.GET or None, user=self.request.user)

    def get_search_result(self):
        data = [
            {
                'annee_academique': '1',
                'code': '2',
                'intitule': '3',
            },
            {
                'annee_academique': '1',
                'code': '2',
                'intitule': '3',
            },
        ]  # TODO :: message_bus.invoke(Command)
        return data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, formset):
        # TODO :: to implement
        # cmd = Command(...)
        # message__bus.invoke(cmd)
        # display_error_messages(self.request, messages)
        # display_success_messages(self.request, messages)
        # self.render_to_response(self.get_context_data(form=self.get_form(self.form_class)))
        return super().form_valid(formset)

    def get_success_url(self):
        # TODO :: redirect to pae main page
        return ""

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'search_form': self.get_search_form(),
            'search_result': self.get_search_result(),
            'intitule_groupement': "MAT1ECGE - Formation pluridisciplinaires en sciences humaines",
            'intitule_programme': 'ECGE1BA - 2021-2022'
        }
