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

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from base.models.utils.utils import ChoiceEnum
from base.utils.htmx import HtmxMixin
from mockup.views.event_modeling import data


class SensDeplacement(ChoiceEnum):
    HAUT = _("HAUT")
    BAS = _("BAS")


class DeplacerUniteEnseignementForm(forms.Form):
    code_ue = forms.CharField(widget=forms.HiddenInput())
    groupement_contenant = forms.CharField(widget=forms.HiddenInput())
    sens_deplacement = forms.ChoiceField(choices=list(SensDeplacement.choices()), widget=forms.HiddenInput())


class DeplacerHautUniteEnseignementFormView(HtmxMixin, LoginRequiredMixin, FormView):
    name = 'deplacer-ue'

    # FormView
    template_name = "mockup/blocks/tab_contenu.html"
    form_class = DeplacerUniteEnseignementForm

    # HtmxMixin
    htmx_template_name = "mockup/blocks/tab_contenu.html"

    def form_valid(self, form: DeplacerUniteEnseignementForm):
        code_ue = form.cleaned_data['code_ue']
        groupement_contenant = form.cleaned_data['groupement_contenant']
        index_code_ue = next((index for (index, d) in enumerate(data) if d["code_ue"] == code_ue), None)
        if form.cleaned_data['sens_deplacement'] == SensDeplacement.HAUT.name:
            data.insert(index_code_ue-1, data.pop(index_code_ue))
        elif form.cleaned_data['sens_deplacement'] == SensDeplacement.BAS.name:
            data.insert(index_code_ue+1, data.pop(index_code_ue))
        # TODO :: to implement
        # cmd = Command(...)
        # message__bus.invoke(cmd)
        # display_error_messages(self.request, messages)
        # display_success_messages(self.request, messages)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(self.name)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'search_result': data,
        }
