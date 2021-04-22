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
import functools
import operator
from typing import List

from django.db.models import Q, F

from attribution.models.attribution import Attribution
from ddd.logic.learning_unit.dtos import ScoreResponsibleDTO
from learning_unit.ddd.domain.learning_unit_year_identity import LearningUnitYearIdentity


def score_responsible_search(learning_unit_identities: List[LearningUnitYearIdentity]) -> List[ScoreResponsibleDTO]:
    luy_identity_clauses = [_build_identity_clause(identity) for identity in learning_unit_identities]
    luy_identity_filter_clause = functools.reduce(operator.or_, luy_identity_clauses)

    queryset = Attribution.objects.filter(score_responsible=True)
    queryset = queryset.filter(luy_identity_filter_clause).annotate(
        last_name=F('tutor__person__last_name'),
        first_name=F('tutor__person__first_name'),
        email=F('tutor__person__email'),
        code=F('learning_unit_year__acronym'),
        year=F('learning_unit_year__academic_year__year')
        )
    queryset = queryset.values(
        "last_name",
        "first_name",
        "email",
        "code",
        "year"
    )

    result = []
    for data_dict in queryset.values():
        result.append(ScoreResponsibleDTO(
            last_name=data_dict['last_name'],
            first_name=data_dict['first_name'],
            email=data_dict['email'],
            code=data_dict['code'],
            year=data_dict['year'],
        ))
    return result


def _build_identity_clause(learning_unit_identity: 'LearningUnitYearIdentity') -> Q:
    return Q(learning_unit_year__acronym=learning_unit_identity.code,
             learning_unit_year__academic_year__year=learning_unit_identity.year)
