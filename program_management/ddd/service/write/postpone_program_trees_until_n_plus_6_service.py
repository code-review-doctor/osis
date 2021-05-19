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
from education_group.ddd.service.write import copy_group_service
from infrastructure.shared_kernel.academic_year.repository import academic_year as academic_year_repository
from program_management.ddd.command import PostponeProgramTreesUntilNPlus6Command
from program_management.ddd.domain.program_tree import ProgramTreeIdentity
from program_management.ddd.domain.service import postpone_until_n_plus_6
from program_management.ddd.repositories import program_tree as program_tree_repo


def postpone_program_trees_until_n_plus_6(cmd: PostponeProgramTreesUntilNPlus6Command) -> List['ProgramTreeIdentity']:
    repo = program_tree_repo.ProgramTreeRepository()
    current_academic_year = GetCurrentAcademicYear().get_starting_academic_year(
        datetime.date.today(),
        academic_year_repository.AcademicYearRepository()

    )

    trees_to_postpone = repo.search_last_occurence(current_academic_year.year)

    result = []
    for tree in trees_to_postpone:
        trees_created = postpone_until_n_plus_6.Postpone().postpone_program_tree(current_academic_year, tree, repo)

        result += [
            repo.create(tree_created, copy_group_service=copy_group_service.copy_group)
            for tree_created in trees_created
        ]

    return result
