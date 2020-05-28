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

from education_group.ddd.domain.training import TrainingIdentity
from education_group.models.group_year import GroupYear
from osis_common.ddd.interface import BusinessException
from program_management.ddd.business_types import *

DomainService = object  # TODO :: move into osis_commin/ddd/interfaces


class TrainingIdentitySearch(DomainService):
    def get_from_node_identity(self, node_identity: 'NodeIdentity') -> 'TrainingIdentity':
        values = GroupYear.objects.filter(
            partial_acronym=node_identity.code,
            academic_year__year=node_identity.year
        ).annotate(
            offer_acronym=F('education_group_version__education_group_year__acronym'),
            year=F('education_group_version__education_group_year__academic_year__year'),
        ).values('offer_acronym', 'year')
        if values:
            return TrainingIdentity(acronym=values[0]['offer_acronym'], year=values[0]['year'])
        raise BusinessException(
            "TrainingIdentity not found from NodeIdentity = {n_id.code} - {n_id.year}".format(n_id=node_identity)
        )

    def get_from_program_tree_version_identity(self, tree_version_identity) -> 'TrainingIdentity':
        return TrainingIdentity(
            acronym=tree_version_identity.offer_acronym,
            year=tree_version_identity.year,
        )
