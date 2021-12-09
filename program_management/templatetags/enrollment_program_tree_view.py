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
from typing import List

from django.templatetags.static import static
from django.utils.safestring import mark_safe

from base.templatetags.education_group import register
from program_management.ddd.business_types import *

# TODO :: Remove this file and move the code into a Serializer

OPTIONAL_PNG = static('img/education_group_year/optional.png')
MANDATORY_PNG = static('img/education_group_year/mandatory.png')

CHILD_BRANCH = """\
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


@register.filter
def tree_list(formation: 'FormationDTO'):
    # TODO : To be completed only one level of group for the moment - Need a complete algorithm
    return mark_safe(list_formatter(formation.programme_detaille.groupements))


def list_formatter(groupements: List['GroupementCatalogueDTO']):
    output = []
    for groupement in groupements:
        append_output(groupement, output)
    return '\n'.join(output)


def append_output(groupement: 'GroupementCatalogueDTO', output):
    output.append(
        CHILD_BRANCH.format(
            padding=5,
            icon_list_2=get_mandatory_picture(groupement),
            value=groupement.intitule,
            remark=groupement.remarque if groupement.remarque else '',
            comment=groupement.commentaire if groupement.commentaire else ''
        )
    )


def get_mandatory_picture(groupement: 'GroupementCatalogueDTO'):
    return MANDATORY_PNG if groupement.obligatoire else OPTIONAL_PNG
