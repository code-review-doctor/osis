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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List, Optional

from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYear
from osis_common.ddd import interface
from program_management.ddd.domain.program_tree import ProgramTree, ProgramTreeBuilder
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion, ProgramTreeVersionBuilder
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository

DEFAULT_YEARS_TO_POSTPONE = 6


class PostponeTrees(interface.DomainService):
    @classmethod
    def postpone_program_tree(
            cls,
            current_academic_year: 'AcademicYear',
            from_tree: 'ProgramTree',
            tree_repository: 'ProgramTreeRepository'
    ) -> List['ProgramTree']:
        year_to_postpone_until_to = cls._compute_postponement_until_year(
            current_academic_year,
            from_tree.root_node.end_year
        )

        result = []
        tree_to_copy = from_tree
        for year in range(from_tree.entity_id.year, year_to_postpone_until_to):
            tree_to_copy = ProgramTreeBuilder().copy_to_next_year(
                copy_from=tree_to_copy,
                repository=tree_repository
            )
            result.append(tree_to_copy)
        return result

    @classmethod
    def postpone_program_tree_version(
            cls,
            current_academic_year: 'AcademicYear',
            from_tree_version: 'ProgramTreeVersion',
            tree_repository: 'ProgramTreeVersionRepository'
    ) -> List['ProgramTreeVersion']:
        year_to_postpone_until_to = cls._compute_postponement_until_year(
            current_academic_year,
            from_tree_version.end_year_of_existence
        )

        result = []
        tree_version_to_copy = from_tree_version
        for year in range(from_tree_version.entity_id.year, year_to_postpone_until_to):
            tree_version_to_copy = ProgramTreeVersionBuilder().copy_to_next_year(
                copy_from=tree_version_to_copy,
                tree_version_repository=tree_repository
            )
            result.append(tree_version_to_copy)
        return result

    @classmethod
    def _compute_postponement_until_year(cls, current_academic_year: 'AcademicYear', end_year: Optional[int]) -> int:
        max_postponement_year = current_academic_year.year + DEFAULT_YEARS_TO_POSTPONE
        return min(max_postponement_year, end_year) if end_year else max_postponement_year
