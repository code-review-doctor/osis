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
    GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    IdentiteGroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjoutee
from ddd.logic.preparation_programme_annuel_etudiant.dtos import GroupementAjusteFromRepositoryDTO
from education_group.ddd.domain.group import GroupIdentity
from osis_common.ddd import interface
from osis_common.ddd.interface import ApplicationService
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity


class IGroupementAjusteInscriptionCoursRepository(interface.AbstractRepository):
    @classmethod
    def get(cls, entity_id: 'IdentiteGroupementAjusteInscriptionCours') -> 'GroupementAjusteInscriptionCours':
        pass

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteGroupementAjusteInscriptionCours']] = None,
            programme_id: 'GroupIdentity' = None,
            groupement_id: 'GroupIdentity' = None,
            **kwargs
    ) -> List['GroupementAjusteInscriptionCours']:
        pass

    @classmethod
    def delete(cls, entity_id: 'IdentiteGroupementAjusteInscriptionCours', **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    def save(cls, entity: 'GroupementAjusteInscriptionCours') -> None:
        pass

    @classmethod
    def get_dtos(
            cls,
            program_tree_version_identity: ProgramTreeVersionIdentity
    ) -> List['GroupementAjusteFromRepositoryDTO']:
        pass

    @classmethod
    def search_ue_ajustee_en_ajout(
            cls,
            code_unite_enseignement: str,
            programme_id: 'GroupIdentity',
            groupement_id: 'GroupIdentity'
    ) -> 'UniteEnseignementAjoutee':
        pass

    @classmethod
    def search_ue_ajustee_en_modification(
            cls,
            code_unite_uuid: str,
            programme_id: 'GroupIdentity',
            groupement_id: 'GroupIdentity'
    ) -> 'UniteEnseignementModifiee':
        pass

    @classmethod
    def search_ue_ajustee_en_suppression(
            cls,
            code_unite_enseignement_uuid: str,
            programme_id: 'GroupIdentity',
            groupement_id: 'GroupIdentity'
    ) -> 'UniteEnseignementSupprimee':
        pass

    @classmethod
    def delete_ajustement_ajout(cls, entity: 'UniteEnseignementAjoutee') -> None:
        pass

    @classmethod
    def delete_ajustement_modification(cls, entity: 'UniteEnseignementModifiee') -> None:
        pass

    @classmethod
    def delete_ajustement_suppression(cls, entity: 'UniteEnseignementSupprimee') -> None:
        pass
