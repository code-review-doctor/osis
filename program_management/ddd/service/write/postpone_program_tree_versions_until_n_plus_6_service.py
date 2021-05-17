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
import datetime
from typing import List

from ddd.logic.shared_kernel.academic_year.domain.service.get_current_academic_year import GetCurrentAcademicYear
from infrastructure.shared_kernel.academic_year.repository import academic_year as academic_year_repository
from program_management.ddd.command import PostponeProgramTreeVersionsUntilNPlus6Command
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.domain.service import postpone_until_n_plus_6
from program_management.ddd.repositories import program_tree_version as program_tree_version_repo


def postpone_program_tree_versions_until_n_plus_6(
        cmd: PostponeProgramTreeVersionsUntilNPlus6Command
) -> List['ProgramTreeVersionIdentity']:
    repo = program_tree_version_repo.ProgramTreeVersionRepository()
    current_academic_year = GetCurrentAcademicYear().get_starting_academic_year(
        datetime.date.today(),
        academic_year_repository.AcademicYearRepository()

    )

    tree_versions_to_postpone = repo.search_last_occurence(current_academic_year.year)

    result = []
    for tree_version in tree_versions_to_postpone:
        trees_created = postpone_until_n_plus_6.Postpone().postpone_program_tree_version(
            current_academic_year,
            tree_version,
            repo
        )

        result += [repo.create(tree_created) for tree_created in trees_created]

    return result
