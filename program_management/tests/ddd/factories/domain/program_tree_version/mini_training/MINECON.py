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
import factory

from base.models.enums.education_group_types import GroupType, MiniTrainingType
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.ddd.repositories import program_tree_version as program_tree_version_repository
from program_management.models.enums.node_type import NodeType
from program_management.tests.ddd.factories.program_tree import tree_builder
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory


class MINECONTreeFactory(factory.Factory):
    class Meta:
        model = ProgramTree
        abstract = False

    current_year = 2018
    end_year = 2025
    persist = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> 'ProgramTree':
        return cls.produce_tree(*args, **kwargs)

    @classmethod
    def produce_tree(cls, current_year: int, end_year: int, persist: bool) -> 'ProgramTree':
        tree_data = {
            "node_type": MiniTrainingType.ACCESS_MINOR,
            "year": current_year,
            "end_year": end_year,
            "code": "LECON100I",
            "title": "MINECON",
            "children": [
                {
                    "node_type": GroupType.COMMON_CORE,
                    "year": current_year,
                    "end_year": end_year,
                    "code": "LECON100T",
                    "title": "PARTIEDEBASEMINECON",
                    "children": [
                        {
                            "node_type": GroupType.SUB_GROUP,
                            "year": current_year,
                            "end_year": end_year,
                            "code": "LECON101R",
                            "title": "MINBASEECO",
                            "children": [
                                {
                                    "node_type": NodeType.LEARNING_UNIT,
                                    "year": current_year,
                                    "end_date": end_year,
                                    "code": "LECON1101",
                                },
                                {
                                    "node_type": NodeType.LEARNING_UNIT,
                                    "year": current_year,
                                    "end_date": end_year,
                                    "code": "LECON1102",
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        tree = tree_builder(tree_data, persist)

        return tree


class MINECONFactory(ProgramTreeVersionFactory):
    tree = factory.SubFactory(MINECONTreeFactory)

    @factory.post_generation
    def persist(obj, create, extracted, **kwargs):
        program_tree_version_repository.ProgramTreeVersionRepository.create(obj)
