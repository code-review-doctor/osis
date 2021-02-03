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
import contextlib
from typing import List

from osis_common.ddd.interface import BusinessException
from program_management.ddd.business_types import *
from program_management.ddd.command import CopyTreeVersionToNextYearCommand, CopyProgramTreeToNextYearCommand
from program_management.ddd.service.write import copy_program_version_service, \
    copy_program_tree_content_service


def bulk_copy_program_tree_version(cmds: List[CopyTreeVersionToNextYearCommand]) -> List['ProgramTreeVersionIdentity']:
    result = []
    for cmd in cmds:
        with contextlib.suppress(BusinessException):
            copy_program_tree_cmd = CopyProgramTreeToNextYearCommand(code=cmd.from_offer_code, year=cmd.from_year)
            copy_program_tree_content_service.copy_program_tree_content_to_next_year(copy_program_tree_cmd)
            result.append(copy_program_version_service.copy_tree_version_to_next_year(cmd))

    return result
