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
import itertools
from typing import Optional, List

from education_group.ddd.domain import exception
from education_group.ddd.repository import mini_training as mini_training_repository


class InMemoryMiniTrainingRepository(mini_training_repository.MiniTrainingRepository):
    _mini_trainings = list()  # type: List['MiniTraining']

    @classmethod
    def create(cls, mini_training: 'MiniTraining', **_) -> 'MiniTrainingIdentity':
        cls._mini_trainings.append(mini_training)
        return mini_training.entity_id

    @classmethod
    def update(cls, mini_training: 'MiniTraining', **_) -> 'MiniTrainingIdentity':
        if mini_training not in cls._mini_trainings:
            raise exception.MiniTrainingNotFoundException()
        return mini_training.entity_id

    @classmethod
    def get(cls, entity_id: 'MiniTrainingIdentity') -> 'MiniTraining':
        result = next(
            (mini_training for mini_training in cls._mini_trainings if mini_training.entity_id == entity_id),
            None
        )
        if not result:
            raise exception.MiniTrainingNotFoundException()
        return result

    @classmethod
    def search(cls, entity_ids: Optional[List['MiniTrainingIdentity']] = None, **kwargs) -> List['MiniTraining']:
        if entity_ids:
            return [mini_training for mini_training in cls._mini_trainings if mini_training.entity_id in entity_ids]
        return []

    @classmethod
    def delete(cls, entity_id: 'MiniTrainingIdentity', **_) -> None:
        mini_training_to_delete = next(
            (mini_training for mini_training in cls._mini_trainings if mini_training.entity_id == entity_id),
            None
        )
        if mini_training_to_delete:
            cls._mini_trainings.remove(mini_training_to_delete)

    @classmethod
    def search_mini_trainings_last_occurence(cls, from_year: int) -> List['MiniTraining']:
        datas = (root_entity for root_entity in cls._mini_trainings if root_entity.entity_id.year >= from_year)
        group_by_acronym = itertools.groupby(datas, lambda training: training.acronym)
        return [max(mini_training, key=lambda mini: mini.year) for acronym, mini_training in group_by_acronym]
