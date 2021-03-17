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

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from osis_common.ddd.interface import BusinessException
from program_management.ddd.business_types import *
from program_management.ddd.command import FillTreeVersionContentFromPastYearCommand, \
    FillProgramTreeTransitionContentFromProgramTreeVersionCommand
from program_management.ddd.domain import program_tree_version
from program_management.ddd.domain.exception import ProgramTreeVersionNotFoundException
from program_management.ddd.service.write import fill_program_tree_version_content_from_last_year_service, \
    fill_program_tree_transition_content_from_program_tree_version_service


def bulk_fill_program_tree_version_content_from_last_year(
        cmds: List[FillTreeVersionContentFromPastYearCommand]
) -> List['ProgramTreeVersionIdentity']:
    result = []
    for cmd in cmds:
        with contextlib.suppress(BusinessException, MultipleBusinessExceptions, ProgramTreeVersionNotFoundException):
            if cmd.to_transition_name != program_tree_version.NOT_A_TRANSITION:
                result.append(
                    fill_program_tree_transition_content_from_program_tree_version_service.
                    fill_program_tree_transition_content_from_program_tree_version(
                        FillProgramTreeTransitionContentFromProgramTreeVersionCommand(
                            from_year=cmd.to_year - 1,
                            from_version_name=cmd.to_version_name,
                            from_offer_acronym=cmd.to_offer_acronym,
                            from_transition_name=cmd.to_transition_name,
                            to_year=cmd.to_year,
                            to_version_name=cmd.to_version_name,
                            to_offer_acronym=cmd.to_offer_acronym,
                            to_transition_name=cmd.to_transition_name
                        )
                    )
                )
            else:
                result.append(
                    fill_program_tree_version_content_from_last_year_service.
                    fill_program_tree_version_content_from_last_year(cmd)
                )

    return result
