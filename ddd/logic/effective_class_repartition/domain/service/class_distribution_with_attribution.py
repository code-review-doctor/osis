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
from typing import List

from ddd.logic.effective_class_repartition.builder.tutor_identity_builder import TutorIdentityBuilder
from ddd.logic.effective_class_repartition.domain.service.i_tutor_attribution import \
    ITutorAttributionToLearningUnitTranslator
from ddd.logic.effective_class_repartition.dtos import TutorClassRepartitionDTO, TutorAttributionToLearningUnitDTO
from ddd.logic.effective_class_repartition.repository.i_tutor import ITutorRepository
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from osis_common.ddd import interface


class ClassDistributionWithAttribution(interface.DomainService):

    @classmethod
    def search_by_effective_class(
            cls,
            effective_class_identity: 'EffectiveClassIdentity',
            tutor_attribution_translator: 'ITutorAttributionToLearningUnitTranslator',
            tutor_repository: 'ITutorRepository'
    ) -> List['TutorClassRepartitionDTO']:
        attributions = tutor_attribution_translator.search_attributions_to_learning_unit(
            effective_class_identity.learning_unit_identity
        )

        result = []
        for tutor in tutor_repository.search(effective_class_identity=effective_class_identity):
            result.extend(_get_tutor_class_repartition_dtos(tutor, attributions))

        return _order_tutors_by_last_name_and_first_name(result)

    @classmethod
    def search_by_matricule_enseignant(
            cls,
            matricule_enseignant: str,
            annee: int,
            tutor_attribution_translator: 'ITutorAttributionToLearningUnitTranslator',
            tutor_repository: 'ITutorRepository'
    ) -> List['TutorClassRepartitionDTO']:
        tutor_identity = TutorIdentityBuilder.build_from_personal_id_number(matricule_enseignant)
        tutor = tutor_repository.get(entity_id=tutor_identity)
        if not tutor:
            return []

        attribution_uuids = {
            distributed_class.attribution.uuid
            for distributed_class in tutor.distributed_effective_classes
            if distributed_class.effective_class.learning_unit_identity.year == annee
            # FIXME :: ajouter 'annee' dans l'aggregat Tutor ????
        }
        attributions = tutor_attribution_translator.search_learning_unit_attributions(attribution_uuids)
        return _get_tutor_class_repartition_dtos(tutor, attributions)


def _order_tutors_by_last_name_and_first_name(
        result: List['TutorClassRepartitionDTO']
) -> List['TutorClassRepartitionDTO']:
    def last_name_first_name(tutor: 'TutorClassRepartitionDTO') -> str:
        return tutor.last_name + tutor.first_name

    result = sorted(result, key=last_name_first_name)
    return result


def _get_tutor_class_repartition_dtos(tutor, attributions: List['TutorAttributionToLearningUnitDTO']):
    liste_repartition_dtos = []
    for class_repartition in tutor.distributed_effective_classes:
        attribution = next(
            att for att in attributions if att.attribution_uuid == class_repartition.attribution.uuid
        )
        dto = TutorClassRepartitionDTO(
            attribution_uuid=class_repartition.attribution.uuid,
            last_name=attribution.last_name,
            first_name=attribution.first_name,
            function=attribution.function,
            distributed_volume_to_class=class_repartition.distributed_volume,
            personal_id_number=tutor.entity_id.personal_id_number,
            complete_class_code=class_repartition.effective_class.complete_class_code,
            annee=class_repartition.effective_class.learning_unit_identity.year,
        )
        liste_repartition_dtos.append(dto)
    return liste_repartition_dtos
