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
from django.db.models import F

from education_group.models.group_year import GroupYear
from osis_common.ddd.interface import BusinessException
from program_management.ddd.business_types import *
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity

DomainService = object  # TODO :: move into osis_commin/ddd/interfaces


class ProgramTreeVersionIdentitySearch(DomainService):
    def get_from_node_identity(self, node_identity: 'NodeIdentity') -> 'ProgramTreeVersionIdentity':
        values = GroupYear.objects.filter(
            partial_acronym=node_identity.code,
            academic_year__year=node_identity.year
        ).annotate(
            offer_acronym=F('educationgroupversion__offer__acronym'),
            year=F('academic_year__year'),
            version_name=F('educationgroupversion__version_name'),
            is_transition=F('educationgroupversion__is_transition'),
        ).values('offer_acronym', 'year', 'version_name', 'is_transition')
        if values:
            return ProgramTreeVersionIdentity(**values[0])
        raise BusinessException("Program tree version identity not found")
