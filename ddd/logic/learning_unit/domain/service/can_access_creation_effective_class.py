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

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from ddd.logic.learning_unit.domain.validator.exceptions import ClassTypeInvalidException, \
    LearningUnitHasPartimException, LearningUnitHasProposalException, \
    LearningUnitHasEnrollmentException, LearningUnitHasNoVolumeException
from ddd.logic.learning_unit.repository.i_learning_unit import ILearningUnitRepository
from osis_common.ddd import interface


class CanCreateEffectiveClass(interface.DomainService):

    @classmethod
    def raise_if_can_not_access(
            cls,
            learning_unit: 'LearningUnit',
            learning_unit_repository: 'ILearningUnitRepository',
    ):
        exceptions = set()  # type Set[BusinessException]
        if learning_unit.is_external():
            exceptions.add(ClassTypeInvalidException())

        if learning_unit.has_partim():
            exceptions.add(LearningUnitHasPartimException())

        if learning_unit_repository.has_proposal_this_year_or_in_past(learning_unit):
            exceptions.add(LearningUnitHasProposalException())

        if learning_unit_repository.has_enrollments(learning_unit):
            exceptions.add(LearningUnitHasEnrollmentException())

        if not learning_unit.has_volume():
            exceptions.add(LearningUnitHasNoVolumeException())

        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)
