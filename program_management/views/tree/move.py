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
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from waffle.decorators import waffle_flag

import program_management.ddd.service.write.up_link_service
from base.models.education_group_year import EducationGroupYear
from base.models.group_element_year import GroupElementYear
from base.views.common import display_success_messages
from base.views.education_groups import perms
from osis_common.utils.models import get_object_or_none
from program_management.ddd.service.write import down_link_service
from program_management.models.enums import node_type


#  TODO take path as only parameter
@login_required
@waffle_flag("education_group_update")
@require_http_methods(['POST'])
def up(request, root_id, link_id):
    return _order_content(request, root_id, link_id, program_management.ddd.service.write.up_link_service.up_link)


@login_required
@waffle_flag("education_group_update")
@require_http_methods(['POST'])
def down(request, root_id, link_id):
    return _order_content(request, root_id, link_id, down_link_service.down_link)


def _order_content(
        request: HttpRequest,
        root_id: int,
        link_id: int,
        order_function
):
    # FIXME When perm refactored remove this code so as to use ddd domain objects
    group_element_year = get_object_or_none(GroupElementYear, pk=link_id)
    perms.can_change_education_group(request.user, group_element_year.parent)

    child_node_type = node_type.NodeType.EDUCATION_GROUP if isinstance(group_element_year.child, EducationGroupYear) \
        else node_type.NodeType.LEARNING_UNIT
    order_function(root_id, group_element_year.parent.id, group_element_year.child.id, child_node_type)

    success_msg = _("The %(acronym)s has been moved") % {'acronym': group_element_year.child.acronym}
    display_success_messages(request, success_msg)

    http_referer = request.META.get('HTTP_REFERER')
    return redirect(http_referer)


