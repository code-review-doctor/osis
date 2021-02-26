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
from typing import List, Dict, Any

from base.models import group_element_year
from base.models.enums.link_type import LinkTypes
from base.models.enums.quadrimesters import DerogationQuadrimester
from program_management.ddd.business_types import *
from program_management.ddd.domain import program_tree
from program_management.ddd.domain.link import factory as link_factory, LinkIdentity
# Typing
from program_management.ddd.domain.prerequisite import Prerequisites, NullPrerequisites
from program_management.ddd.repositories import load_node, load_authorized_relationship

GroupElementYearColumnName = str
LinkKey = str  # <parent_id>_<child_id>  Example : "123_124"
NodeKey = int  # Element.pk
TreeStructure = List[Dict[GroupElementYearColumnName, Any]]


def __load_tree_nodes(tree_structure: TreeStructure) -> Dict[NodeKey, 'Node']:
    element_ids = [link['child_id'] for link in tree_structure]
    nodes_list = load_node.load_multiple(element_ids)
    return {n.pk: n for n in nodes_list}


def __convert_link_type_to_enum(link_data: dict) -> None:
    link_type = link_data['link_type']
    if link_type:
        link_data['link_type'] = LinkTypes[link_type]


def __convert_quadrimester_to_enum(gey_dict: dict) -> None:
    if gey_dict.get('quadrimester_derogation'):
        gey_dict['quadrimester_derogation'] = DerogationQuadrimester[gey_dict['quadrimester_derogation']]


def __load_tree_links(tree_structure: TreeStructure) -> Dict[LinkKey, 'Link']:
    group_element_year_ids = [link['id'] for link in tree_structure]
    group_element_year_qs = group_element_year.GroupElementYear.objects.filter(pk__in=group_element_year_ids).values(
        'pk',
        'relative_credits',
        'min_credits',
        'max_credits',
        'access_condition',
        'is_mandatory',
        'block',
        'comment',
        'comment_english',
        'own_comment',
        'quadrimester_derogation',
        'link_type',
        'parent_element_id',
        'child_element_id',
        'order'
    )

    tree_links = {}
    for gey_dict in group_element_year_qs:
        parent_id = gey_dict.pop('parent_element_id')
        child_id = gey_dict.pop('child_element_id')
        __convert_link_type_to_enum(gey_dict)
        __convert_quadrimester_to_enum(gey_dict)

        tree_id = '_'.join([str(parent_id), str(child_id)])
        tree_links[tree_id] = link_factory.get_link(parent=None, child=None, **gey_dict)
    return tree_links


def __build_tree(
        root_node: 'Node',
        tree_structure: TreeStructure,
        nodes: Dict[NodeKey, 'Node'],
        links: Dict[LinkKey, 'Link'],
        prerequisites_of_all_trees: List['Prerequisites']
) -> 'ProgramTree':
    structure_by_parent = {}  # For performance
    for s_dict in tree_structure:
        if s_dict['path']:  # TODO :: Case child_id or parent_id is null - to remove after DB null constraint set
            parent_path = '|'.join(s_dict['path'].split('|')[:-1])
            structure_by_parent.setdefault(parent_path, []).append(s_dict)
    root_node.children = __build_children(str(root_node.pk), structure_by_parent, nodes, links)
    tree = program_tree.ProgramTree(
        root_node,
        authorized_relationships=load_authorized_relationship.load(),
    )
    tree.prerequisites = next(
        (prereq for prereq in prerequisites_of_all_trees if prereq.context_tree == tree.entity_id),
        NullPrerequisites(context_tree=tree.entity_id)
    )
    return tree


def __build_children(
        root_path: 'Path',
        map_parent_path_with_tree_structure: Dict['Path', TreeStructure],
        nodes: Dict[NodeKey, 'Node'],
        links: Dict[LinkKey, 'Link']
) -> List['Link']:
    children = []
    for child_structure in map_parent_path_with_tree_structure.get(root_path) or []:
        child_id = child_structure['child_id']
        parent_id = child_structure['parent_id']
        child_node = nodes[child_id]

        if not child_node.children:
            # "if" condition for performance : avoid recursivity if the children of the node have already been computed
            child_node.children = __build_children(
                child_structure['path'],
                map_parent_path_with_tree_structure,
                nodes,
                links
            )

        link_node = links['_'.join([str(parent_id), str(child_node.pk)])]

        link_node.parent = nodes[parent_id]
        link_node.child = child_node
        link_node.entity_id = LinkIdentity(
            parent_code=link_node.parent.code,
            child_code=link_node.child.code,
            parent_year=link_node.parent.year,
            child_year=link_node.child.year
        )
        children.append(link_node)
    return children


def _get_root_ids(child_element_ids: list, link_type: LinkTypes = None) -> List[int]:
    if child_element_ids:
        assert isinstance(child_element_ids, list)
    if not child_element_ids:
        return []

    qs = group_element_year.GroupElementYear.objects.get_reverse_adjacency_list(
        child_element_ids=child_element_ids,
        link_type=link_type,
    )
    if not qs:
        return []
    all_parents = set(obj["parent_id"] for obj in qs)
    parent_by_child = {
        obj["child_id"]: obj["parent_id"] for obj in qs
    }
    return set(
        parent_id for parent_id in all_parents
        if not parent_by_child.get(parent_id)
    )
