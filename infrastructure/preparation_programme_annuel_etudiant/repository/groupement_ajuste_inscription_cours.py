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

from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    IdentiteGroupementAjusteInscriptionCours, GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_modifiee import \
    UniteEnseignementModifiee
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_supprimee import \
    UniteEnseignementSupprimee
from ddd.logic.preparation_programme_annuel_etudiant.dtos import GroupementAjusteFromRepositoryDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from osis_common.ddd.interface import ApplicationService
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity


class GroupementAjusteInscriptionCoursRepository(IGroupementAjusteInscriptionCoursRepository):
    @classmethod
    def get_dtos(
            cls,
            program_tree_version_identity: ProgramTreeVersionIdentity
    ) -> List['GroupementAjusteFromRepositoryDTO']:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'IdentiteGroupementAjusteInscriptionCours') -> 'GroupementAjusteInscriptionCours':
        raise NotImplementedError

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteGroupementAjusteInscriptionCours']] = None,
            **kwargs
    ) -> List['GroupementAjusteInscriptionCours']:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: 'IdentiteGroupementAjusteInscriptionCours', **kwargs: ApplicationService) -> None:
        raise NotImplementedError

    @classmethod
    def save(cls, entity: 'GroupementAjusteInscriptionCours') -> None:
        raise NotImplementedError

    @classmethod
    def search_ue_ajustee_en_ajout(
            cls,
            code_unite_enseignement: str,
            programme_id: 'GroupIdentity',
            groupement_id: 'GroupIdentity',
            entity_ids: Optional[List['IdentiteGroupementAjusteInscriptionCours']] = None,
            **kwargs
    ) -> 'UniteEnseignementAjoutee':
        raise NotImplementedError

    @classmethod
    def search_ue_ajustee_en_modification(
            cls,
            code_unite_uuid: str,
            programme_id: 'GroupIdentity',
            groupement_id: 'GroupIdentity',
            **kwargs
    ) -> 'UniteEnseignementModifiee':
        raise NotImplementedError

    @classmethod
    def search_ue_ajustee_en_suppression(
            cls,
            code_unite_enseignement: str,
            programme_id: 'GroupIdentity',
            groupement_id: 'GroupIdentity',
            entity_ids: Optional[List['IdentiteGroupementAjusteInscriptionCours']] = None,
            **kwargs
    ) -> 'UniteEnseignementSupprimee':
        raise NotImplementedError

    @classmethod
    def delete_ajustement_ajout(cls, entity: 'UniteEnseignementAjoutee') -> None:
        raise NotImplementedError

    @classmethod
    def delete_ajustement_modification(cls, entity: 'UniteEnseignementModifiee') -> None:
        raise NotImplementedError

    @classmethod
    def delete_ajustement_suppression(cls, entity: 'UniteEnseignementSupprimee') -> None:
        raise NotImplementedError
