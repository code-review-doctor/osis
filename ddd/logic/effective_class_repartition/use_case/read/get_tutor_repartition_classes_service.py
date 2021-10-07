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

from ddd.logic.effective_class_repartition.builder.tutor_identity_builder import TutorIdentityBuilder
from ddd.logic.effective_class_repartition.commands import GetTutorRepartitionClassesCommand
from ddd.logic.effective_class_repartition.domain.model.tutor import Tutor
from ddd.logic.effective_class_repartition.repository.i_tutor import ITutorRepository


# TODO :: unit test
def get_tutor_repartition_classes(
        cmd: 'GetTutorRepartitionClassesCommand',
        tutor_repository: 'ITutorRepository'
) -> 'Tutor':
    tutor_identity = TutorIdentityBuilder.build_from_personal_id_number(cmd.tutor_personal_id_number)
    return tutor_repository.get(tutor_identity)
