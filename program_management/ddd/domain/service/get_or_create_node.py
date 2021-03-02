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

import attr

from education_group.ddd.command import CreateOrphanGroupCommand
from education_group.ddd.service.write import create_group_service
from osis_common.ddd import interface
from program_management.ddd.business_types import *
from program_management.ddd.domain import node
from program_management.ddd.domain.exception import NodeNotFoundException
from program_management.ddd.repositories import node as node_repository


class GetOrCreateNode(interface.DomainService):
    @classmethod
    def from_node(cls, source_node: 'Node', to_year: int) -> 'Node':
        repo = node_repository.NodeRepository()

        node_identity = attr.evolve(source_node.entity_id, year=to_year)

        try:
            existing_node = repo.get(node_identity)
        except NodeNotFoundException:
            existing_node = None

        if existing_node:
            return existing_node

        result = node.factory.copy_to_year(source_node, to_year, source_node.code)
        if not source_node.is_learning_unit():
            cls._create_group(result)
        return result

    @classmethod
    def _create_group(cls, n: 'NodeGroupYear'):
        create_group_service.create_orphan_group(
            CreateOrphanGroupCommand(
                code=n.code,
                year=n.year,
                type=n.node_type.name,
                abbreviated_title=n.title,
                title_fr=n.group_title_fr,
                title_en=n.group_title_en,
                credits=int(n.credits) if n.credits else None,
                constraint_type=n.constraint_type.name if n.constraint_type else None,
                min_constraint=n.min_constraint,
                max_constraint=n.max_constraint,
                management_entity_acronym=n.management_entity_acronym,
                teaching_campus_name=n.teaching_campus.name,
                organization_name=n.teaching_campus.university_name,
                remark_fr=n.remark_fr or "",
                remark_en=n.remark_en or "",
                start_year=n.start_year,
                end_year=n.end_year,
            )
        )
