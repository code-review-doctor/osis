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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import Set

from ddd.logic.encodage_des_notes.soumission.domain.service.i_entites_cohorte import IEntitesCohorteTranslator
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import EntiteNonValidePourAdresseException
from ddd.logic.encodage_des_notes.soumission.dtos import EntiteDTO
from ddd.logic.shared_kernel.entite.domain.model.entite import Entite
from ddd.logic.shared_kernel.entite.repository.entite import IEntiteRepository
from osis_common.ddd import interface


class EntiteAdresseFeuilleDeNotes(interface.DomainService):

    @classmethod
    def get(
            cls,
            nom_cohorte: str,
            entite_repository: 'IEntiteRepository',
            entites_cohorte_translator: 'IEntitesCohorteTranslator'
    ) -> Set['EntiteDTO']:
        identites = entites_cohorte_translator.search(nom_cohorte)

        entites_avec_hierarchie = entite_repository.search_with_parents(identites)

        entite_de_type_faculte = [entite for entite in entites_avec_hierarchie if entite.est_faculte()]
        return {cls._convert_entite_to_dto(entite) for entite in entite_de_type_faculte}.union(
            {cls._convert_entite_to_dto(entite) for entite in entites_avec_hierarchie if entite.entity_id in identites}
        )

    @classmethod
    def verifier_est_valide(
            cls,
            nom_cohorte: str,
            sigle_entite: str,
            entite_repository: 'IEntiteRepository',
            entites_cohorte_translator: 'IEntitesCohorteTranslator'
    ):
        if not sigle_entite:
            return
        entites_valides = cls.get(nom_cohorte, entite_repository, entites_cohorte_translator)
        sigles_valides = [entite.sigle for entite in entites_valides]
        if sigle_entite not in sigles_valides:
            raise EntiteNonValidePourAdresseException()

    @classmethod
    def _convert_entite_to_dto(cls, entite: 'Entite') -> 'EntiteDTO':
        return EntiteDTO(
            sigle=entite.sigle,
            sigle_parent=entite.sigle_du_parent,
            type=entite.type
        )
