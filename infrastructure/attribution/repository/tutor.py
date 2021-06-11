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
from typing import List, Optional

from django.db.models import F, QuerySet

from attribution.models.attribution_charge_new import AttributionChargeNew as AttributionChargeNewDatabase
from ddd.logic.attribution.builder.tutor_builder import TutorBuilder
from ddd.logic.attribution.domain.model._attribution import LearningUnitAttribution, LearningUnitAttributionIdentity
from ddd.logic.attribution.domain.model._class_volume_repartition import ClassVolumeRepartition
from ddd.logic.attribution.domain.model.tutor import Tutor
from ddd.logic.attribution.dtos import TutorSearchDTO
from ddd.logic.attribution.repository.i_tutor import ITutorRepository
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.dtos import EffectiveClassFromRepositoryDTO
from learning_unit.models.learning_class_year import LearningClassYear as LearningClassYearDatabase
from osis_common.ddd.interface import ApplicationService


class TutorRepository(ITutorRepository):

    @classmethod
    def delete(cls, entity_id: 'TutorIdentity', **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    def get(cls, entity_id: 'TutorIdentity') -> 'Tutor':
        pass

    @classmethod
    def search(cls, entity_ids: Optional[List['TutorIdentity']] = None,
               learning_unit_identity: 'LearningUnitIdentity' = None) -> List['Tutor']:
        qs = AttributionChargeNewDatabase.objects.all()
        qs = qs.filter(
            learning_component_year__learning_unit_year__acronym=learning_unit_identity.code,
            learning_component_year__learning_unit_year__academic_year__year=learning_unit_identity.year,
        ).select_related(
            'learning_component_year',
            'attribution'
        )

        qs = qs.annotate(
            last_name=F('attribution__tutor__person__last_name'),
            first_name=F('attribution__tutor__person__first_name'),
            attribution_function=F('attribution__function'),
            personal_id_number=F('attribution__tutor__person__global_id'),
            attribution_uuid=F('attribution__pk'),
            volume=F('allocation_charge'),
            luy_id=F('learning_component_year__learning_unit_year__pk')
        ).values(
            "last_name",
            "first_name",
            "attribution_function",
            "personal_id_number",
            "attribution_uuid",
            "volume",
            "luy_id"
        ).order_by('attribution__tutor__person__last_name', 'attribution__tutor__person__first_name', )
        # TODO : UUId pas juste
        result = []

        for data_dict in qs.values():
            effective_classes = _get_effective_classes(data_dict['luy_id'])
            result.append(
                TutorBuilder.build_from_repository_dto(
                    TutorSearchDTO(
                        last_name=data_dict['last_name'],
                        first_name=data_dict['first_name'],
                        personal_id_number=data_dict['personal_id_number'],
                        attributions=[
                            LearningUnitAttribution(
                                entity_id=LearningUnitAttributionIdentity(uuid=data_dict['attribution_uuid']),
                                function=data_dict['attribution_function'],
                                learning_unit=learning_unit_identity,
                                distributed_effective_classes=_get_distributed_effective_classes(
                                    data_dict, effective_classes)
                                )
                        ]
                    )
                )
            )
        return result

    @classmethod
    def save(cls, entity: 'Tutor') -> None:
        pass


def _get_effective_classes(learning_unit_year_id: int) -> QuerySet:
    return LearningClassYearDatabase.objects.filter(
        learning_component_year__learning_unit_year__id=learning_unit_year_id
    ).annotate(
        class_code=F('acronym'),
        learning_unit_code=F('learning_component_year__learning_unit_year__acronym'),
        learning_unit_year=F('learning_component_year__learning_unit_year__academic_year__year'),
    ).values(
        'class_code',
        'learning_unit_code',
        'learning_unit_year'
    )


def _get_distributed_effective_classes(data_dict, effective_classes):
    return [
        ClassVolumeRepartition(
            effective_class=EffectiveClassIdentityBuilder.build_from_code_and_learning_unit_identity_data(
                class_code=effective_classe['class_code'],
                learning_unit_code=effective_classe['learning_unit_code'],
                learning_unit_year=effective_classe['learning_unit_year']
            ),
            distributed_volume=data_dict['volume']
        ) for effective_classe in effective_classes
    ]
