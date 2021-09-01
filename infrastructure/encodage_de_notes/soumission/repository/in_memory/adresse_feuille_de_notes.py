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

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import AdresseFeuilleDeNotes, \
    IdentiteAdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository


class AdresseFeuilleDeNotesInMemoryRepository(InMemoryGenericRepository, IAdresseFeuilleDeNotesRepository):
    entities = list()  # type: List[AdresseFeuilleDeNotes]

    @classmethod
    def search_dtos(
            cls,
            entity_ids: Optional[List['IdentiteAdresseFeuilleDeNotes']] = None,
            **kwargs
    ) -> List['AdresseFeuilleDeNotesDTO']:
        adresses = cls.search(entity_ids=entity_ids, **kwargs)
        return [cls._convert_adresse_to_dto(adress) for adress in adresses]

    @classmethod
    def _convert_adresse_to_dto(
            cls,
            adresse: AdresseFeuilleDeNotes,
    ) -> 'AdresseFeuilleDeNotesDTO':
        return AdresseFeuilleDeNotesDTO(
            nom_cohorte=adresse.nom_cohorte,
            entite=adresse.sigle_entite,
            destinataire=adresse.destinataire,
            rue_numero=adresse.rue_numero,
            code_postal=adresse.code_postal,
            ville=adresse.ville,
            pays=adresse.pays,
            telephone=adresse.telephone,
            fax=adresse.fax,
            email=adresse.email,
        )
