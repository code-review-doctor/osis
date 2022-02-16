##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    IdentiteGroupementAjusteInscriptionCours, GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.validator.validators_by_business_action import \
    ReinitialiserProgrammeValidatorList
from ddd.logic.preparation_programme_annuel_etudiant.dtos import GroupementAjusteFromRepositoryDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from education_group.ddd.domain.group import GroupIdentity
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity


class GroupementAjusteInscriptionCoursInMemoryRepository(
    InMemoryGenericRepository,
    IGroupementAjusteInscriptionCoursRepository
):
    dtos = []

    @classmethod
    def get_dtos(
            cls,
            program_tree_version_identity: ProgramTreeVersionIdentity
    ) -> List['GroupementAjusteFromRepositoryDTO']:
        return [
            dto
            for dto in cls.dtos
            if dto.code_groupement == program_tree_version_identity.offer_acronym
            and dto.annee == program_tree_version_identity.year
            and dto.version_programme == program_tree_version_identity.version_name
            and dto.nom_transition == program_tree_version_identity.transition_name
        ]

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteGroupementAjusteInscriptionCours']] = None,
            programme_id: 'GroupIdentity' = None,
            groupement_id: 'GroupIdentity' = None,
            **kwargs
    ) -> List['GroupementAjusteInscriptionCours']:
        result = cls.entities
        if programme_id:
            result = [entity for entity in result if entity.programme_id == programme_id]
        if groupement_id:
            result = [entity for entity in result if entity.groupement_id == groupement_id]
        return result

    @classmethod
    def bulk_delete(cls, entities: List['GroupementAjusteInscriptionCours']) -> None:
        ReinitialiserProgrammeValidatorList(groupements_ajustes=entities).validate()
        for entity in entities:
            cls.delete(entity.entity_id)
