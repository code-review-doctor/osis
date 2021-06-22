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

from ddd.logic.attribution.commands import DistributeClassToTutorCommand
from ddd.logic.attribution.domain.model.tutor import TutorIdentity
from ddd.logic.attribution.domain.service.i_tutor_attribution import ITutorAttributionToLearningUnitTranslator
from ddd.logic.attribution.repository.i_tutor import ITutorRepository


def distribute_class_to_tutor(
        cmd: DistributeClassToTutorCommand,
        repository: 'ITutorRepository',
        tutor_attribution_translator: 'ITutorAttributionToLearningUnitTranslator'
) -> 'TutorIdentity':
    # TODO: to implement
    # TODO: reuse check_class_belongs_to_learning_unit DomainService
    # Tutor().assign_class()
    # if not tutor_attribution_translator.get_tutor_attribution_to_learning_unit():
    #     raise BusinessException()
    return
