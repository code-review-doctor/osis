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
from dal import autocomplete
from dal_select2_tagging.widgets import TaggingSelect2
from django import forms
from django.forms import HiddenInput, BaseFormSet
from django.utils.translation import pgettext_lazy, gettext_lazy as _


from base.forms.utils import choice_field
from base.models.enums.exam_enrollment_justification_type import StateTypes
from base.models.learning_unit_year import LearningUnitYear
from ddd.logic.encodage_des_notes.encodage.commands import GetCohortesGestionnaireCommand
from education_group.forms.fields import UpperCaseCharField
from infrastructure.messages_bus import message_bus_instance


class ScoreEncodingFormSet(BaseFormSet):
    def is_valid(self):
        return not any(form.is_bound and form.has_changed() and not form.is_valid() for form in self.forms)


class ScoreEncodingForm(forms.Form):
    note = UpperCaseCharField(max_length=100, required=False)
    noma = forms.CharField(widget=HiddenInput())

    def clean_note(self):
        note = self.cleaned_data['note']
        if note:
            return note.replace(",", ".")
        return note

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['note'].widget.attrs['style'] = self.fields['note'].widget.attrs['style'] + '; width:70px; '


class ScoreSearchEncodingForm(forms.Form):
    note = UpperCaseCharField(max_length=100, required=False)
    noma = forms.CharField(widget=HiddenInput())
    code_unite_enseignement = forms.CharField(widget=HiddenInput())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['note'].widget.attrs['style'] = 'width:70px; '


class ScoreSearchForm(forms.Form):
    noma = forms.CharField(required=False, label=_("Reg. No."))
    nom = forms.CharField(required=False, label=_("Lastname"))
    prenom = forms.CharField(required=False, label=_("Firstname"))
    etat = forms.ChoiceField(
        choices=choice_field.add_blank(
            StateTypes.choices(),
            blank_choice_display=pgettext_lazy("male plural", "All")
        ),
        required=False,
        label=_("State")
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
        return choice_field.add_blank(tuple(choices), blank_choice_display=pgettext_lazy("male plural", "All"))

    def clean(self):
        cleaned_data = super().clean()
        if not any([
            cleaned_data['noma'],
            cleaned_data['nom'],
            cleaned_data['prenom'],
            cleaned_data['etat'],
            cleaned_data['nom_cohorte'],
        ]):
            self.add_error(None, _("Please choose at least one criteria!"))
        return cleaned_data


class ScoreEncodingProgressFilterForm(forms.Form):
    cohorte_name = forms.MultipleChoiceField(
        required=False,
        label=pgettext_lazy('encoding', 'Program'),
        widget=autocomplete.Select2Multiple(
            url='formations-autocomplete',
            attrs={'data-html': True, 'data-placeholder': _('Acronym/Short title')},
        )
    )
    tutor = forms.ChoiceField(
        required=False,
        label=_('Tutor'),
        widget=autocomplete.ListSelect2(
            url='enseignants-autocomplete',
            attrs={'data-html': True, 'data-placeholder': _('Name')},
        )
    )
    learning_unit_code = forms.ChoiceField(
        required=False, label=_('Learning unit'),
        widget=autocomplete.ListSelect2(
            url='learning-unit-code-autocomplete',
            attrs={'data-html': True, 'data-placeholder': pgettext_lazy('UE acronym', 'Acronym')},
        )
    )
    incomplete_encodings_only = forms.BooleanField(required=False, label=_('Missing score'))

    def __init__(self, matricule_fgs_gestionnaire: str = '', **kwargs):
        super().__init__(**kwargs)
        self.fields['cohorte_name'].choices = self.get_nom_cohorte_choices(matricule_fgs_gestionnaire)
        self.__set_initial_value_to_learning_unit_code()
        self.__set_initial_value_to_tutor()

    def __set_initial_value_to_learning_unit_code(self):
        value_submitted_from_client = self.data.get('learning_unit_code')
        self.fields['learning_unit_code'].initial = value_submitted_from_client
        self.fields['learning_unit_code'].choices = [(value_submitted_from_client, value_submitted_from_client)] or []

    def __set_initial_value_to_tutor(self):
        value_submitted_from_client = self.data.get('tutor')
        self.fields['tutor'].initial = value_submitted_from_client
        self.fields['tutor'].choices = [(value_submitted_from_client, value_submitted_from_client)] or []

    def get_nom_cohorte_choices(self, matricule_fgs_gestionnaire: str):
        cmd = GetCohortesGestionnaireCommand(matricule_fgs_gestionnaire=matricule_fgs_gestionnaire)
        results = message_bus_instance.invoke(cmd)
        choices = (
            (cohorte.nom_cohorte, cohorte.nom_cohorte,) for cohorte in sorted(results, key=lambda x: x.nom_cohorte)
        )
        return choice_field.add_blank(tuple(choices), blank_choice_display=pgettext_lazy("male plural", "All"))
