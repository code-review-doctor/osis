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
from collections import OrderedDict
from typing import List, Union

from django.templatetags.static import static
from django.utils.safestring import mark_safe

from ddd.logic.preparation_programme_annuel_etudiant.dtos import ProgrammeDTO, GroupementCatalogueDTO, \
    UniteEnseignementCatalogueDTO


def tree_list(programme: ProgrammeDTO):

    link_parent_children = _get_parents_and_children(
        _get_parent_groups(programme.groupements),
        programme.ues
    )
    return mark_safe(
        list_formatter(_get_first_level_parents(link_parent_children), link_parent_children)
    )


def _get_first_level_parents(link_parent_children):
    grp_racines = OrderedDict()
    for k, v in link_parent_children.items():
        if k.inclus_dans is None:
            grp_racines.update({k: v})
    return grp_racines


def _get_parent_groups(all_groupement: List[GroupementCatalogueDTO]) -> OrderedDict:
    parents_groups = OrderedDict()
    for g in all_groupement:
        parents_groups.update({g: []})
    return parents_groups


def _get_parents_and_children(
        parents_groups: OrderedDict,
        learning_units: List[UniteEnseignementCatalogueDTO])\
        -> OrderedDict:
    link_parent_children = parents_groups.copy()
    for group, value_children in parents_groups.items():
        if group.inclus_dans:
            children = link_parent_children.get(group.inclus_dans)
            children.append(group)
            link_parent_children.update({group.inclus_dans: children})
    for ue in learning_units:
        if ue.inclus_dans:
            children = link_parent_children.get(ue.inclus_dans)
            children.append(ue)
            link_parent_children.update({ue.inclus_dans: children})
    return link_parent_children


def list_formatter(groups: dict, parent_children: dict, output=[], depth=None):
    depth = depth if depth else 1

    for group, children in groups.items():
        padding = 2 * depth
        if children:
            append_output(group, output, padding)
            grps = OrderedDict()
            for c in children:
                if isinstance(c, UniteEnseignementCatalogueDTO):
                    append_output(c, output, padding + 2)
                else:
                    grps.update({c: parent_children.get(c)})

            if grps:
                list_formatter(grps, parent_children, output, depth=depth + 1)
        else:
            append_output(group, output, padding)

    return '\n'.join(output)


def append_output(
        object: Union[GroupementCatalogueDTO, UniteEnseignementCatalogueDTO], output: List[str], padding: int
):
    if isinstance(object, UniteEnseignementCatalogueDTO):

        output.append(
            CHILD_LEAF.format(
                padding=padding,
                icon_list_2=get_mandatory_picture(object),
                value=object.informations_principales_agregees,
                an_1=check_block(object.bloc, 1),
                an_2=check_block(object.bloc, 2),
                an_3=check_block(object.bloc, 3),
                an_4=check_block(object.bloc, 4),
                an_5=check_block(object.bloc, 5),
                an_6=check_block(object.bloc, 6),

            )
        )
    else:
        output.append(
            CHILD_BRANCH.format(
                padding=padding,
                icon_list_2=get_mandatory_picture(object),
                value=object.informations_principales_agregees,
                remark=object.remarque if object.remarque else '',
            )
        )


def get_mandatory_picture(object: Union['GroupementCatalogueDTO', 'UniteEnseignementCatalogueDTO']):
    return MANDATORY_PNG if object.obligatoire else OPTIONAL_PNG


def check_block(bloc, value):
    return "X" if bloc and str(value) in str(bloc) else ""


def _get_inscription_formulaire_affichage_arbre(formation_dto):
    max_blocks = _get_number_of_distinct_blocks(formation_dto.programme)
    return {
        'max_block': max_blocks,
        'main_part_col_length': get_main_part_col_length(max_blocks),
        'tree_list': tree_list(formation_dto.programme)
    }


MAX_NUMBER_OF_BLOCK = 6
CURRENT_SIZE_FOR_ANNUAL_COLUMN = 15
MAIN_PART_INIT_SIZE = 650
PADDING = 10
USUAL_NUMBER_OF_BLOCKS = 3
OPTIONAL_PNG = static('img/education_group_year/optional.png')
MANDATORY_PNG = static('img/education_group_year/mandatory.png')
VALIDATE_CASE_JPG = static('img/education_group_year/validate_case.jpg')
INVALIDATE_CASE_JPG = static('img/education_group_year/invalidate_case.png')
DELTA = static('img/education_group_year/delta.png')
ACTIVITY_DISPENSED = static('img/education_group_year/bisannual_even.png')
ACTIVITY_NOT_DISPENSED = static('img/education_group_year/bisannual_odd.png')
PREREQUIS = static('img/education_group_year/prerequis.gif')
CHILD_BRANCH = """\
<tr>
    <td style="padding-left:{padding}em;"> 
        <div style="word-break: keep-all;">
            <img src="{icon_list_2}" height="10" width="10">            
            {value} <br>
            {remark}            
        </div>
    </td>
</tr>
"""
CHILD_LEAF = """\
<tr>
    <td style="padding-left:{padding}em;">
        <div style="word-break: keep-all;">            
            <img src="{icon_list_2}" height="10" width="10">            
            {value}                        
        </div>
    </td>
    <td style="text-align: center;">{an_1}</td>
    <td style="text-align: center;">{an_2}</td>
    <td style="text-align: center;">{an_3}</td>
    <td style="text-align: center;">{an_4}</td>
    <td style="text-align: center;">{an_5}</td>
    <td style="text-align: center;">{an_6}</td>    
</tr>
"""


def _get_number_of_distinct_blocks(program):
    blocks = set()
    for ue in program.ues:
        if ue.bloc:
            blocks.add(ue.bloc)
    return len(blocks)


def get_main_part_col_length(max_block):
    if max_block <= USUAL_NUMBER_OF_BLOCKS:
        return MAIN_PART_INIT_SIZE
    else:
        return MAIN_PART_INIT_SIZE - ((max_block - USUAL_NUMBER_OF_BLOCKS) * (CURRENT_SIZE_FOR_ANNUAL_COLUMN + PADDING))
