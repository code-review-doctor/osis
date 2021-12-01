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
from typing import List, Optional, Tuple

import attr

from assessments.models.enums.score_sheet_address_choices import ScoreSheetAddressEntityType
from base.utils.itertools import filter_duplicate
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_entites_cohorte import IEntitesCohorteTranslator
from ddd.logic.shared_kernel.entite.domain.model.entiteucl import EntiteUCL
from ddd.logic.shared_kernel.entite.dtos import EntiteDTO
from ddd.logic.shared_kernel.entite.repository.entiteucl import IEntiteUCLRepository
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class EntitesPossiblesAdresseFeuilleDeNotesDTO:
    gestion = attr.ib(type='EntiteUCL')
    gestion_faculte = attr.ib(type=Optional['EntiteUCL'])
    administration = attr.ib(type='EntiteUCL')
    administration_faculte = attr.ib(type=Optional['EntiteUCL'])

    @property
    def choix(self) -> List[Tuple[str, str]]:
        entites_possibles = [self.gestion, self.administration, self.gestion_faculte, self.administration_faculte]
        types_entites_possibles = [
            ScoreSheetAddressEntityType.ENTITY_MANAGEMENT.value,
            ScoreSheetAddressEntityType.ENTITY_ADMINISTRATION.value,
            ScoreSheetAddressEntityType.ENTITY_MANAGEMENT_PARENT.value,
            ScoreSheetAddressEntityType.ENTITY_ADMINISTRATION_PARENT.value,
        ]

        choix = [
            (type_entite, "{} - {}".format(entite.sigle, entite.intitule))
            for entite, type_entite in zip(entites_possibles, types_entites_possibles)
            if entite
        ]

        return filter_duplicate(choix, lambda option: option[1])

    def get_par_type(self, type_entite: str) -> Optional['EntiteUCL']:
        if type_entite == ScoreSheetAddressEntityType.ENTITY_ADMINISTRATION.value:
            return self.administration
        elif type_entite == ScoreSheetAddressEntityType.ENTITY_MANAGEMENT.value:
            return self.gestion
        elif type_entite == ScoreSheetAddressEntityType.ENTITY_ADMINISTRATION_PARENT.value:
            return self.administration_faculte
        return self.gestion_faculte


class EntiteAdresseFeuilleDeNotes(interface.DomainService):
    @classmethod
    def search(
            cls,
            nom_cohorte: str,
            entite_repository: 'IEntiteUCLRepository',
            entites_cohorte_translator: 'IEntitesCohorteTranslator',
            periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
    ) -> EntitesPossiblesAdresseFeuilleDeNotesDTO:
        annee_academique = periode_soumission_note_translator.get().annee_concernee
        identites_administration_et_gestion = entites_cohorte_translator.search_entite_administration_et_gestion(
            nom_cohorte,
            annee_academique
        )
        entite_administration_avec_sa_hierarchie = entite_repository.search_with_parents(
            [identites_administration_et_gestion.administration]
        )
        entite_administration = next(
            entite for entite in entite_administration_avec_sa_hierarchie
            if entite.entity_id == identites_administration_et_gestion.administration
        )
        faculte_entite_administration = next(
            (entite for entite in entite_administration_avec_sa_hierarchie
             if entite.est_faculte() and entite.entity_id != identites_administration_et_gestion.administration),
            None
        )

        entite_gestion_avec_sa_hierarchie = entite_repository.search_with_parents(
            [identites_administration_et_gestion.gestion]
        )
        entite_gestion = next(
            (entite for entite in entite_gestion_avec_sa_hierarchie
             if entite.entity_id == identites_administration_et_gestion.gestion),
            None
        )
        faculte_entite_gestion = next(
            (entite for entite in entite_gestion_avec_sa_hierarchie
             if entite.est_faculte() and entite.entity_id != identites_administration_et_gestion.gestion),
            None
        )

        return EntitesPossiblesAdresseFeuilleDeNotesDTO(
            gestion=entite_gestion,
            gestion_faculte=faculte_entite_gestion,
            administration=entite_administration,
            administration_faculte=faculte_entite_administration
        )

    @classmethod
    def _convert_entite_to_dto(cls, entite: 'EntiteUCL') -> 'EntiteDTO':
        return EntiteDTO(
            sigle=entite.sigle,
            intitule=entite.intitule,
            sigle_parent=entite.sigle_du_parent,
            type=entite.type
        )
