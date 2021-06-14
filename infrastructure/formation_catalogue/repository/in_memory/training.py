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
from education_group.ddd.repository import training as training_repository


class InMemoryTrainingRepository(training_repository.TrainingRepository):
    _trainings = list()  # type: List['Training']

    @classmethod
    def create(cls, training: 'Training', **_) -> 'TrainingIdentity':
        cls._trainings.append(training)
        return training.entity_id

    @classmethod
    def update(cls, training: 'Training', **_) -> 'TrainingIdentity':
        if training not in cls._trainings:
            raise exception.TrainingNotFoundException()
        return training.entity_id

    @classmethod
    def get(cls, entity_id: 'TrainingIdentity') -> 'Training':
        result = next(
            (training for training in cls._trainings if training.entity_id == entity_id),
            None
        )
        if not result:
            raise exception.TrainingNotFoundException()
        return result

    @classmethod
    def search(cls, entity_ids: Optional[List['TrainingIdentity']] = None, **kwargs) -> List['Training']:
        if entity_ids:
            return [training for training in cls._trainings if training.entity_id in entity_ids]
        return []

    @classmethod
    def delete(cls, entity_id: 'TrainingIdentity', **_) -> None:
        training_to_delete = next((training for training in cls._trainings if training.entity_id == entity_id), None)
        if training_to_delete:
            cls._trainings.remove(training_to_delete)

    @classmethod
    def search_trainings_last_occurence(cls, from_year: int) -> List['Training']:
        datas = (root_entity for root_entity in cls._trainings if root_entity.entity_id.year >= from_year)
        group_by_acronym = itertools.groupby(datas, lambda training: training.acronym)
        return [max(trainings, key=lambda training: training.year) for acronym, trainings in group_by_acronym]
