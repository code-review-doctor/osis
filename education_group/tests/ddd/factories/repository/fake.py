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
import itertools
from typing import List, Type

from education_group.ddd.business_types import *
from education_group.ddd.domain import exception
from testing.mocks import FakeRepository


def get_fake_group_repository(root_entities: List['Group']) -> Type['FakeRepository']:
    class_name = "FakeGroupRepository"
    return type(class_name, (FakeRepository,), {
        "root_entities": root_entities.copy(),
        "not_found_exception_class": exception.GroupNotFoundException,
        "search_groups_last_occurence": search_groups_last_occurence
    })


def get_fake_mini_training_repository(root_entities: List['MiniTraining']) -> Type['FakeRepository']:
    class_name = "FakeMiniTrainingRepository"
    return type(class_name, (FakeRepository,), {
        "root_entities": root_entities.copy(),
        "not_found_exception_class": exception.MiniTrainingNotFoundException,
        "search_mini_trainings_last_occurence": search_trainings_last_occurence
    })


def get_fake_training_repository(root_entities: List['Training']) -> Type['FakeRepository']:
    class_name = "FakeTrainingRepository"
    return type(class_name, (FakeRepository,), {
        "root_entities": root_entities.copy(),
        "not_found_exception_class": exception.TrainingNotFoundException,
        "search_trainings_last_occurence": search_trainings_last_occurence
    })


@classmethod
def search_trainings_last_occurence(cls, from_year: int) -> List['Training']:
    datas = (root_entity for root_entity in cls.root_entities if root_entity.entity_id.year >= from_year)
    group_by_acronym = itertools.groupby(datas, lambda training: training.acronym)
    return [max(trainings, key=lambda training: training.year) for acronym, trainings in group_by_acronym]


@classmethod
def search_groups_last_occurence(cls, from_year: int) -> List['Group']:
    datas = (root_entity for root_entity in cls.root_entities if root_entity.entity_id.year >= from_year)
    group_by_code = itertools.groupby(datas, lambda group: group.code)
    return [max(groups, key=lambda group: group.year) for acronym, groups in group_by_code]
