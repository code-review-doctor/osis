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
from django.utils.translation import gettext_lazy as _

from backoffice.settings.base import MINIMUM_LUE_YEAR
from ddd.logic.shared_kernel.academic_year.commands import SearchAcademicYearCommand
from education_group.forms.fields import UpperCaseCharField
from infrastructure.messages_bus import message_bus_instance


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
        all_academic_year = message_bus_instance.invoke(SearchAcademicYearCommand(year=MINIMUM_LUE_YEAR))
        self.fields['annee_academique'].choices = [(ac_year.year, str(ac_year)) for ac_year in all_academic_year]
