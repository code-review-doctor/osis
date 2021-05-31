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
from typing import Optional, List

from django.db.models import F

from base.models.campus import Campus as CampusModelDB
from base.models.enums.organization_type import MAIN
from ddd.logic.shared_kernel.campus.builder.uclouvain_campus_builder import UclouvainCampusBuilder
from ddd.logic.shared_kernel.campus.domain.model.uclouvain_campus import UclouvainCampusIdentity, UclouvainCampus
from ddd.logic.shared_kernel.campus.dtos import UclouvainCampusDataDTO
from ddd.logic.shared_kernel.campus.repository.i_uclouvain_campus import IUclouvainCampusRepository
from osis_common.ddd.interface import ApplicationService


class UclouvainCampusRepository(IUclouvainCampusRepository):
    @classmethod
    def get(cls, entity_id: UclouvainCampusIdentity) -> 'UclouvainCampus':
        raise NotImplementedError

    @classmethod
    def search(cls, entity_ids: Optional[List['UclouvainCampusIdentity']] = None, **kwargs) -> List['UclouvainCampus']:
        qs = _get_common_queryset()
        qs = annotate_qs(qs)
        objects_as_dict = _values_qs(qs).order_by('name')
        return [
            UclouvainCampusBuilder.build_from_repository_dto(UclouvainCampusDataDTO(**obj_as_dict))
            for obj_as_dict in objects_as_dict
        ]

    @classmethod
    def delete(cls, entity_id: 'UclouvainCampusIdentity', **kwargs: ApplicationService) -> None:
        raise NotImplementedError

    @classmethod
    def save(cls, entity: 'UclouvainCampus') -> None:
        raise NotImplementedError


def _get_common_queryset():
    return CampusModelDB.objects.filter(organization__type=MAIN)


def annotate_qs(qs):
    return qs.annotate(
        organization_name=F('organization__name'),
    )


def _values_qs(qs):
    return qs.values(
        'uuid',
        'name',
        'organization_name',
    )
