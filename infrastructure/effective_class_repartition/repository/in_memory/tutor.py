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
from typing import List, Optional

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.effective_class_repartition.domain.model.tutor import Tutor, TutorIdentity
from ddd.logic.effective_class_repartition.repository.i_tutor import ITutorRepository
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity


class TutorRepository(InMemoryGenericRepository, ITutorRepository):
    entities = list()  # type: List[Tutor]

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['TutorIdentity']] = None,
            effective_class_identity: 'EffectiveClassIdentity' = None,
    ) -> List['Tutor']:
        return list(
            filter(
                lambda tutor: _filter(tutor, entity_ids, effective_class_identity),
                cls.entities
            )
        )


def _filter(
        tutor: 'Tutor',
        entity_ids: Optional[List['TutorIdentity']],
        effective_class_identity: 'EffectiveClassIdentity'
):
    class_identities = [class_repartition.effective_class for class_repartition in tutor.distributed_effective_classes]
    if effective_class_identity and effective_class_identity in class_identities:
        return True
    if entity_ids and tutor.entity_id in entity_ids:
        return True
    return False
