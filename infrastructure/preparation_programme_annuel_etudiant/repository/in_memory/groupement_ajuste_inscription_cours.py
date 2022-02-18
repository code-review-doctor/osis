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
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjoutee
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_modifiee import \
    UniteEnseignementModifiee
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
    def search_ue_ajustee_en_ajout(
            cls,
            code_unite_enseignement: str,
            programme_id: 'GroupIdentity',
            groupement_id: 'GroupIdentity'
    ) -> 'UniteEnseignementAjoutee':
        objects = cls.search(programme_id=programme_id, groupement_id=groupement_id)
        for obj in objects:
            for ue in obj.unites_enseignement_ajoutees:
                if ue.code == code_unite_enseignement:
                    return ue

    @classmethod
    def search_ue_ajustee_en_modification(
            cls,
            code_unite_uuid: str,
            programme_id: 'GroupIdentity',
            groupement_id: 'GroupIdentity',

    ) -> 'UniteEnseignementModifiee':
        objects = cls.search(programme_id=programme_id, groupement_id=groupement_id)

        for obj in objects:
            for ue in obj.unites_enseignement_modifiees:
                if ue.entity_id.uuid == code_unite_uuid.uuid:
                    return ue

    @classmethod
    def search_ue_ajustee_en_suppression(
            cls,
            code_unite_enseignement_uuid: str,
            programme_id: 'GroupIdentity',
            groupement_id: 'GroupIdentity',
    ) -> 'UniteEnseignementSupprimee':
        objects = cls.search(programme_id=programme_id, groupement_id=groupement_id)
        for obj in objects:
            for ue in obj.unites_enseignement_supprimees:
                if ue.entity_id.uuid == code_unite_enseignement_uuid.uuid:
                    return ue

    @classmethod
    def delete_ajustement_ajout(cls, entity: 'UniteEnseignementAjoutee') -> None:
        for dto in cls.entities:
            for ue in dto.unites_enseignement_ajoutees:
                if ue.code == entity.code:
                    dto.unites_enseignement_ajoutees.remove(ue)

                    return None
        return None

    @classmethod
    def delete_ajustement_modification(cls, entity: 'UniteEnseignementModifiee') -> None:
        for dto in cls.entities:
            for ue in dto.unites_enseignement_modifiees:
                if ue.entity_id.uuid == entity.entity_id.uuid:
                    dto.unites_enseignement_modifiees.remove(ue)
                    return None
        return None

    @classmethod
    def delete_ajustement_suppression(cls, entity: 'UniteEnseignementSupprimee') -> None:
        for dto in cls.entities:
            for ue in dto.unites_enseignement_supprimees:
                if ue.entity_id.uuid == entity.entity_id.uuid:
                    dto.unites_enseignement_supprimees.remove(ue)
                    return None
        return None
