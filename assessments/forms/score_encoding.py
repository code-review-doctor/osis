##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.forms import HiddenInput
from django.utils.translation import pgettext_lazy, gettext_lazy as _


from base.forms.utils import choice_field
from base.models.enums.exam_enrollment_justification_type import JustificationTypes
from ddd.logic.encodage_des_notes.encodage.commands import GetCohortesGestionnaireCommand
from infrastructure.messages_bus import message_bus_instance


class ScoreEncodingForm(forms.Form):
    note = forms.CharField(max_length=100, required=False)
    noma = forms.CharField(widget=HiddenInput())


class ScoreSearchForm(forms.Form):
    noma = forms.CharField(required=False)
    nom = forms.CharField(required=False)
    prenom = forms.CharField(required=False)
    justification = forms.ChoiceField(
        choices=choice_field.add_blank(
            JustificationTypes.choices(),
            blank_choice_display=pgettext_lazy("male plural", "All")
        ),
        required=False
    )
    nom_cohorte = forms.ChoiceField(required=False, label=pgettext_lazy('encoding', 'Program'))

    def __init__(self, matricule_fgs_gestionnaire: str = '', **kwargs):
        super().__init__(**kwargs)
        self.fields['nom_cohorte'].choices = self.get_nom_cohorte_choices(matricule_fgs_gestionnaire)

    def get_nom_cohorte_choices(self, matricule_fgs_gestionnaire: str):
        cmd = GetCohortesGestionnaireCommand(matricule_fgs_gestionnaire=matricule_fgs_gestionnaire)
        results = message_bus_instance.invoke(cmd)
        choices = (
            (cohorte.nom_cohorte, cohorte.nom_cohorte,) for cohorte in sorted(results, key=lambda x: x.nom_cohorte)
        )
        return choice_field.add_blank(tuple(choices))

    def clean(self):
        if not any([
            self.cleaned_data['noma'],
            self.cleaned_data['nom'],
            self.cleaned_data['prenom'],
            self.cleaned_data['justification'],
            self.cleaned_data['nom_cohorte'],
        ]):
            self.add_error(None, _("Please choose at least one criteria!"))
        return super().clean()
