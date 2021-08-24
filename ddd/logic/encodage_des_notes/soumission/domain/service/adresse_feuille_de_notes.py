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
from typing import List

from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_identity_builder import \
    AdresseFeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import AdresseFeuilleDeNotes, \
    AdresseFeuilleDeNotesSpecifique, AdresseFeuilleDeNotesBaseeSurEntite
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from ddd.logic.shared_kernel.entite.repository.entite import IEntiteRepository
from osis_common.ddd import interface


class AdresseFeuilleDeNotesDomainService(interface.DomainService):
    @classmethod
    def get_dtos(
            cls,
            noms_cohorte: List[str],
            adresse_feuille_de_notes_repo: 'IAdresseFeuilleDeNotesRepository',
            entite_repo: 'IEntiteRepository'
    ) -> List[AdresseFeuilleDeNotesDTO]:
        identity_builder = AdresseFeuilleDeNotesIdentityBuilder()
        identites_adresse = [identity_builder.build_from_nom_cohorte(nom_cohorte) for nom_cohorte in noms_cohorte]
        adresses = adresse_feuille_de_notes_repo.search(identites_adresse)
        return [cls._convert_adresse_to_dto(adresse, entite_repo) for adresse in adresses]

    @classmethod
    def get_dto(
            cls,
            nom_cohorte: str,
            adresse_feuille_de_notes_repo: 'IAdresseFeuilleDeNotesRepository',
            entite_repo: 'IEntiteRepository'
    ) -> AdresseFeuilleDeNotesDTO:
        return cls.get_dtos([nom_cohorte], adresse_feuille_de_notes_repo, entite_repo)[0]

    @classmethod
    def _convert_adresse_to_dto(
            cls,
            adresse: AdresseFeuilleDeNotes,
            entite_repo: 'IEntiteRepository',
    ) -> 'AdresseFeuilleDeNotesDTO':
        if isinstance(adresse, AdresseFeuilleDeNotesSpecifique):
            return AdresseFeuilleDeNotesDTO(
                nom_cohorte=adresse.nom_cohorte,
                entite="",
                destinataire=adresse.destinataire,
                rue_numero=adresse.rue_numero,
                code_postal=adresse.code_postal,
                ville=adresse.ville,
                pays=adresse.pays,
                telephone=adresse.telephone,
                fax=adresse.fax,
                email=adresse.email,
            )
        elif isinstance(adresse, AdresseFeuilleDeNotesBaseeSurEntite):
            entite = entite_repo.get(adresse.entite)
            return AdresseFeuilleDeNotesDTO(
                nom_cohorte=adresse.nom_cohorte,
                entite=adresse.sigle_entite,
                destinataire="{} - {}".format(adresse.sigle_entite, entite.intitule),
                rue_numero=entite.adresse.rue_numero,
                code_postal=entite.adresse.code_postal,
                ville=entite.adresse.ville,
                pays=entite.adresse.pays,
                telephone=entite.adresse.telephone,
                fax=entite.adresse.fax,
                email=adresse.email,
            )
