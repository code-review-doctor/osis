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

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from base.views import teaching_material
from learning_unit.views.utils import learning_unit_year_getter
from osis_role.contrib.views import permission_required


@login_required
@require_http_methods(['POST', 'GET'])
@permission_required('base.can_edit_learningunit_pedagogy', fn=learning_unit_year_getter, raise_exception=True)
def create_teaching_material(request, learning_unit_year_id):
    return teaching_material.create_view(request, learning_unit_year_id)


@login_required
@require_http_methods(['POST', 'GET'])
@permission_required('base.can_edit_learningunit_pedagogy', fn=learning_unit_year_getter, raise_exception=True)
def update_teaching_material(request, learning_unit_year_id, teaching_material_id):
    return teaching_material.update_view(request, learning_unit_year_id, teaching_material_id)


@login_required
@require_http_methods(['POST', 'GET'])
@permission_required('base.can_edit_learningunit_pedagogy', fn=learning_unit_year_getter, raise_exception=True)
def delete_teaching_material(request, learning_unit_year_id, teaching_material_id):
    return teaching_material.delete_view(request, learning_unit_year_id, teaching_material_id)
