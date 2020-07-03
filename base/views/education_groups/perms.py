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
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import GroupType
from education_group.models.group_year import GroupYear
from osis_role.errors import get_permission_error
from program_management.ddd.domain.node import Node
from program_management.ddd.repositories import load_tree


def can_change_education_group(user, education_group):
    perm = 'base.change_link_data'
    if not user.has_perm(perm, education_group):
        raise PermissionDenied(get_permission_error(user, perm))
    return True


def can_change_general_information(view_func):
    def get_object(node: Node):
        if node.node_type.name in GroupType.get_names():
            return get_object_or_404(
                GroupYear,
                element__pk=node.pk
            )
        else:
            return get_object_or_404(
                EducationGroupYear,
                educationgroupversion__root_group__element__pk=node.pk
            )

    def f_can_change_general_information(request, *args, **kwargs):
        tree = load_tree.load(kwargs['education_group_year_id'])
        node = tree.root_node
        object = get_object(node)
        # education_group_year = get_object_or_404(EducationGroupYear, pk=kwargs['education_group_year_id'])
        perm_name = 'base.change_commonpedagogyinformation' \
            if (node.node_type.name not in GroupType.get_names() and object.is_common) \
            else 'base.change_pedagogyinformation'
        if not request.user.has_perm(perm_name, object):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return f_can_change_general_information


def can_change_admission_condition(view_func):
    def f_can_change_admission_condition(request, *args, **kwargs):
        if kwargs.get('education_group_year_id'):
            education_group_year = get_object_or_404(EducationGroupYear, pk=kwargs['education_group_year_id'])
        else:
            education_group_year = get_object_or_404(EducationGroupYear,
                                                     partial_acronym=kwargs['code'],
                                                     academic_year__year=kwargs['year'])

        perm_name = 'base.change_commonadmissioncondition' if education_group_year.is_common else \
            'base.change_admissioncondition'
        if not request.user.has_perm(perm_name, education_group_year):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return f_can_change_admission_condition
