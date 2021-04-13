# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from base.ddd.utils import business_validator
from program_management.ddd.business_types import *
from program_management.ddd.domain import exception
from program_management.ddd.domain.service import has_specific_version_with_greater_end_year, \
    has_transition_version_with_greater_end_year


class CheckVersionsEndDateValidator(business_validator.BusinessValidator):
    def __init__(self, tree_version: 'ProgramTreeVersion'):
        self.tree_version = tree_version
        super().__init__()

    def validate(self, *args, **kwargs):
        if self.tree_version.is_official_standard:
            exists = has_specific_version_with_greater_end_year.HasSpecificVersionWithGreaterEndYear.\
                specific_version_greater_than_standard_year(self.tree_version)
            if exists:
                raise exception.CannotDeleteStandardDueToSpecificVersionEndDate(self.tree_version)

            exists = has_transition_version_with_greater_end_year.HasTransitionVersionWithGreaterEndYear.\
                transition_version_greater_than_standard_year(self.tree_version)
            if exists:
                raise exception.CannotDeleteStandardDueToTransitionVersionEndDate(self.tree_version)
        elif self.tree_version.is_specific_official:
            exists = has_transition_version_with_greater_end_year.HasTransitionVersionWithGreaterEndYear. \
                transition_version_greater_than_specific_version_year(self.tree_version)
            if exists:
                raise exception.CannotDeleteSpecificVersionDueToTransitionVersionEndDate(self.tree_version)
