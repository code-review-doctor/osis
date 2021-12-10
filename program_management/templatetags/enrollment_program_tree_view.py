############################################################################
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
############################################################################
from collections import OrderedDict
from typing import Union, List

from django.templatetags.static import static
from django.utils.safestring import mark_safe

from base.templatetags.education_group import register
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ProgrammeDetailleDTO, \
    GroupementCatalogueDTO, UniteEnseignementCatalogueDTO

OPTIONAL_PNG = static('img/education_group_year/optional.png')
MANDATORY_PNG = static('img/education_group_year/mandatory.png')
CHILD_BRANCH2 = """\
<tr>
    <td style="padding-left:{padding}em;"> 
        <div style="word-break: keep-all;">
            <img src="{icon_list_2}" height="10" width="10">            
            {value} <br>
            {remark}
            {comment}            
        </div>
    </td>
</tr>
"""
CHILD_LEAF2 = """\
<tr>
    <td style="padding-left:{padding}em;">
        <div style="word-break: keep-all;">
            {value}
        </div>
    </td>
</tr>
"""


@register.filter
def tree_list(programme: ProgrammeDetailleDTO):
    # TODO : To be completed
    link_parent_children = _get_parents_and_children(
        _get_parent_groups(programme.groupements),
        programme.unites_enseignement
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
            grps = {}
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
            CHILD_LEAF2.format(
                padding=padding,
                value="{} {}".format(object.code, object.intitule_complet),

            )
        )
    else:
        output.append(
            CHILD_BRANCH2.format(
                padding=padding,
                icon_list_2=get_mandatory_picture(object),
                value=object.intitule,
                remark=object.remarque if object.remarque else '',
                comment=object.commentaire if object.commentaire else ''

            )
        )


def get_mandatory_picture(groupement: 'GroupementCatalogueDTO'):
    return MANDATORY_PNG if groupement.obligatoire else OPTIONAL_PNG
