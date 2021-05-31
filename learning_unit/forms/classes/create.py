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
from osis_common.forms.widgets import DecimalFormatInput
from base.models.enums import quadrimesters, learning_unit_year_session


class ClassForm(forms.Form):

    acronym = forms.CharField(max_length=1, required=True, label=_('Code'))

    title_fr = forms.CharField(max_length=255, required=False, label=_('Title in French'))
    title_en = forms.CharField(max_length=255, required=False, label=_('Title in French'))

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
        queryset=Campus.objects.all().order_by('name'))
