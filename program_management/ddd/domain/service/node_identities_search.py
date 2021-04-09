##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import List

from django.db.models import F

from education_group.models.group_year import GroupYear
from osis_common.ddd import interface
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity


class NodeIdentitiesSearch(interface.DomainService):
    def search_from_code(self, group_code: str) -> List[NodeIdentity]:
        years = GroupYear.objects.filter(
            group__groupyear__partial_acronym=group_code,
        ).annotate(
            year=F('academic_year__year'),
        ).values_list(
            'year',
            'partial_acronym'
        ).distinct().order_by('year')

        return [NodeIdentity(code=year[1], year=year[0]) for year in years]

    @staticmethod
    def search_from_program_tree_version_identity_for_years(
            program_tree_version_identity: 'ProgramTreeVersionIdentity'
    ) -> List[NodeIdentity]:
        group_years = GroupYear.objects.filter(
            educationgroupversion__offer__acronym=program_tree_version_identity.offer_acronym,
            educationgroupversion__version_name=program_tree_version_identity.version_name,
            educationgroupversion__transition_name=program_tree_version_identity.transition_name,
        ).select_related(
            'educationgroupversion'
        ).annotate(
            year=F('academic_year__year'),
        ).values_list(
            'year',
            'partial_acronym'
        ).distinct().order_by('year')

        return [NodeIdentity(code=group_year[1], year=group_year[0]) for group_year in group_years]
