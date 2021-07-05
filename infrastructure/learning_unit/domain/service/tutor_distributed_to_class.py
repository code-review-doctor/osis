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
from typing import Optional

from ddd.logic.attribution.commands import SearchTutorsDistributedToClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from ddd.logic.learning_unit.domain.service.i_tutor_assigned_to_class import ITutorAssignedToClass


class TutorAssignedToClass(ITutorAssignedToClass):

    @classmethod
    def get_first_tutor_full_name_if_exists(
            cls,
            effective_class_identity: 'EffectiveClassIdentity'
    ) -> Optional[str]:
        from infrastructure.messages_bus import message_bus_instance
        tutors_assigned_to_class = message_bus_instance.invoke(
            SearchTutorsDistributedToClassCommand(
                class_code=effective_class_identity.class_code,
                learning_unit_code=effective_class_identity.learning_unit_identity.code,
                learning_unit_year=effective_class_identity.learning_unit_identity.year
            )
        )
        if tutors_assigned_to_class:
            return tutors_assigned_to_class[0].full_name
