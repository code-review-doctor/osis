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
from django import forms
from django.utils.translation import gettext_lazy as _

from base.forms.learning_unit.edition_volume import VolumeField
from base.models.campus import Campus
from base.utils.mixins_for_forms import DisplayExceptionsByFieldNameMixin
from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from ddd.logic.learning_unit.domain.validator import exceptions
from osis_common.forms.widgets import DecimalFormatInput
from base.models.enums import quadrimesters, learning_unit_year_session


class ClassForm(DisplayExceptionsByFieldNameMixin, forms.Form):

    field_name_by_exception = {
        exceptions.AnnualVolumeInvalidException: ('hourly_volume_partial_q1', 'hourly_volume_partial_q2'),
    }

    class_code = forms.CharField(max_length=1, required=True, label=_('Code'))

    title_fr = forms.CharField(max_length=255, required=True, label=_('Title in French'))
    title_en = forms.CharField(max_length=255, required=False, label=_('Title in English'))

    hourly_volume_partial_q1 = VolumeField(
        label=_('Vol. Q1'),
        widget=DecimalFormatInput(render_value=True),
        required=False,
    )
    hourly_volume_partial_q2 = VolumeField(
        label=_('Vol. Q2'),
        widget=DecimalFormatInput(render_value=True),
        required=False,
    )
    session = forms.ChoiceField(choices=learning_unit_year_session.LEARNING_UNIT_YEAR_SESSION, required=False)
    quadrimester = forms.ChoiceField(choices=quadrimesters.LearningUnitYearQuadrimester.choices(), required=False)

    campus = forms.ModelChoiceField(
        queryset=Campus.objects.all().order_by('name')
    )  # FIXME :: reuse servicebus

    learning_unit_year = forms.ChoiceField(disabled=True)
    learning_unit_code = forms.CharField(disabled=True)
    # learning_unit_type = forms.ChoiceField(disabled=True)
    # internship_subtype = forms.ChoiceField(disabled=True)
    learning_unit_credits = forms.DecimalField(disabled=True)
    # periodicity = forms.ChoiceField(disabled=True)

    def __init__(self, *args, learning_unit: 'LearningUnit' = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.learning_unit = learning_unit
        self.fields['learning_unit_code'].initial = learning_unit.code
        self.fields['learning_unit_year'].choices = [(learning_unit.year, str(learning_unit.entity_id.academic_year))]
        self.fields['learning_unit_year'].initial = learning_unit.year
        self.fields['learning_unit_credits'].initial = learning_unit.credits
        # TODO :: ajouter l'initial pour les utres champs

    def get_command(self) -> CreateEffectiveClassCommand:
        return CreateEffectiveClassCommand(
            class_code=self.cleaned_data['class_code'],
            learning_unit_code=self.learning_unit.code,
            year=self.learning_unit.year,
            title_fr=self.cleaned_data['title_fr'],
            title_en=self.cleaned_data['title_en'],
            place=self.cleaned_data['campus'].name,
            organization_name=self.cleaned_data['campus'].organization.name,  # FIXME
            derogation_quadrimester=self.cleaned_data['quadrimester'],
            session_derogation=self.cleaned_data['session'],
            volume_first_quadrimester=self.cleaned_data['hourly_volume_partial_q1'] or 0,
            volume_second_quadrimester=self.cleaned_data['hourly_volume_partial_q2'] or 0,
        )
