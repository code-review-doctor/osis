##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import Optional, List, Callable

from django.db import transaction

from base.models.group_element_year import GroupElementYear
from education_group.ddd import command
from osis_common.ddd import interface
from osis_common.ddd.interface import Entity
from program_management.ddd.business_types import *
from program_management.ddd.domain.service.identity_search import ProgramTreeVersionIdentitySearch
from program_management.ddd.repositories import persist_tree, load_tree, node
from program_management.models.element import Element


class ProgramTreeRepository(interface.AbstractRepository):

    @classmethod
    def search(cls, entity_ids: Optional[List['ProgramTreeIdentity']] = None, **kwargs) -> List[Entity]:
        raise NotImplementedError

    @classmethod
    def search_from_children(cls, node_ids: List['NodeIdentity'], **kwargs) -> List['ProgramTree']:
        nodes = node.NodeRepository.search(entity_ids=node_ids)
        node_db_ids = [n.node_id for n in nodes]
        return load_tree.load_trees_from_children(node_db_ids, **kwargs)

    @classmethod
    def delete(
            cls,
            entity_id: 'ProgramTreeIdentity',
            delete_orphan_group_service: Callable,
            delete_orphan_training_service: Callable,
            delete_orphan_minitraining_service: Callable
    ) -> None:
        program_tree = cls.get(entity_id)
        links = program_tree.get_all_links()
        nodes = program_tree.get_all_nodes()

        with transaction.atomic():
            GroupElementYear.objects.filter(pk__in=(link.pk for link in links)).delete()
            for node in nodes:
                if node.is_group():
                    cmd = command.DeleteOrphanGroupCommand(code=node.code, year=node.year)
                    delete_orphan_group_service(cmd)
                elif node.is_training():
                    tree_version_id = ProgramTreeVersionIdentitySearch().get_from_node_identity(node.entity_id)
                    cmd = command.DeleteOrphanTrainingCommand(
                        acronym=tree_version_id.offer_acronym,
                        year=tree_version_id.year
                    )
                    delete_orphan_training_service(cmd)
                elif node.is_mini_training():
                    tree_version_id = ProgramTreeVersionIdentitySearch().get_from_node_identity(node.entity_id)
                    cmd = command.DeleteOrphanMiniTrainingCommand(
                        acronym=tree_version_id.offer_acronym,
                        year=tree_version_id.year
                    )
                    delete_orphan_minitraining_service(cmd)

    @classmethod
    def create(cls, program_tree: 'ProgramTree') -> 'ProgramTreeIdentity':
        persist_tree.persist(program_tree)
        return program_tree.entity_id

    @classmethod
    def update(cls, program_tree: 'ProgramTree') -> 'ProgramTreeIdentity':
        persist_tree.persist(program_tree)
        return program_tree.entity_id

    @classmethod
    def get(cls, entity_id: 'ProgramTreeIdentity') -> 'ProgramTree':
        tree_root_id = Element.objects.get(
            group_year__partial_acronym=entity_id.code,
            group_year__academic_year__year=entity_id.year
        ).pk
        return load_tree.load(tree_root_id)
