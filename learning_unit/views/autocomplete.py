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
from typing import List, Dict, Tuple

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin

from base.forms.learning_unit.search.simple import MOBILITY_CHOICE
from base.models.enums.learning_container_year_types import LearningContainerYearType


ID = str
TEXT = str


class LearningUnitTypeAutoComplete(LoginRequiredMixin, autocomplete.Select2ListView):
    def get_list(self) -> List[Tuple[ID, TEXT]]:
        return sorted(
            LearningContainerYearType.choices() + MOBILITY_CHOICE,
            key=lambda container_type: container_type[1]
        )

    def autocomplete_results(self, results: List[Tuple[ID, TEXT]]) -> List[Tuple[ID, TEXT]]:
        return [(id, text) for id, text in results if self.q.lower() in str(text).lower()]

    def results(self, results: List[Tuple[ID, TEXT]]) -> List[Dict]:
        return [dict(id=id, text=text) for id, text in results]
