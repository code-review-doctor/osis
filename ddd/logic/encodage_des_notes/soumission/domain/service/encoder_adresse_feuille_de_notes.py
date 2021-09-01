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
import attr

from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_builder import \
    AdresseFeuilleDeNotesBuilder
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_identity_builder import \
    AdresseFeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.commands import EncoderAdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import IdentiteAdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from ddd.logic.shared_kernel.entite.builder.identite_entite_builder import IdentiteEntiteBuilder
from ddd.logic.shared_kernel.entite.repository.entiteucl import IEntiteUCLRepository
from osis_common.ddd import interface


class EncoderAdresseFeuilleDeNotesDomainService(interface.DomainService):

    @classmethod
    def encoder(
            cls,
            cmd: EncoderAdresseFeuilleDeNotes,
            repo: IAdresseFeuilleDeNotesRepository,
            entite_repository: 'IEntiteUCLRepository',
    ) -> 'IdentiteAdresseFeuilleDeNotes':
        if cmd.entite:
            return cls._encoder_adresse_basee_sur_entite(cmd, repo, entite_repository)
        return cls._encoder_adresse_specifique(cmd, repo)

    @classmethod
    def _encoder_adresse_basee_sur_entite(
            cls,
            cmd: EncoderAdresseFeuilleDeNotes,
            repo: IAdresseFeuilleDeNotesRepository,
            entite_repository: 'IEntiteUCLRepository',
    ) -> 'IdentiteAdresseFeuilleDeNotes':
        identite_entite = IdentiteEntiteBuilder().build_from_sigle(cmd.entite)
        entite = entite_repository.get(identite_entite)

        dto = AdresseFeuilleDeNotesDTO(
            nom_cohorte=cmd.nom_cohorte,
            entite=cmd.entite,
            destinataire="{} - {}".format(entite.sigle, entite.intitule),
            rue_numero=entite.adresse.rue_numero,
            code_postal=entite.adresse.code_postal,
            ville=entite.adresse.ville,
            pays=entite.adresse.pays,
            telephone=entite.adresse.telephone,
            fax=entite.adresse.fax,
            email=cmd.email
        )

        return cls._encoder_adresse(dto, repo)

    @classmethod
    def _encoder_adresse_specifique(
            cls,
            cmd: EncoderAdresseFeuilleDeNotes,
            repo: IAdresseFeuilleDeNotesRepository,
    ) -> 'IdentiteAdresseFeuilleDeNotes':
        dto = AdresseFeuilleDeNotesDTO(
            nom_cohorte=cmd.nom_cohorte,
            entite=cmd.entite,
            destinataire=cmd.destinataire,
            rue_numero=cmd.rue_numero,
            code_postal=cmd.code_postal,
            ville=cmd.ville,
            pays=cmd.pays,
            telephone=cmd.telephone,
            fax=cmd.fax,
            email=cmd.email
        )

        return cls._encoder_adresse(dto, repo)

    @classmethod
    def _encoder_adresse(
            cls,
            dto: AdresseFeuilleDeNotesDTO,
            repo: IAdresseFeuilleDeNotesRepository
    ) -> 'IdentiteAdresseFeuilleDeNotes':
        concerne_un_bachelier = "1BA" in dto.nom_cohorte
        if concerne_un_bachelier:
            return cls._encoder_adresse_pour_bachelier(dto, repo)
        return cls._encoder_adresse_pour_autre_cohortes(dto, repo)

    @classmethod
    def _encoder_adresse_pour_bachelier(
            cls,
            dto: AdresseFeuilleDeNotesDTO,
            repo: IAdresseFeuilleDeNotesRepository,
    ) -> 'IdentiteAdresseFeuilleDeNotes':
        is_adresse_premiere_annee_de_bachelier_identique =\
            cls._is_adresse_bachelier_identique_a_la_premiere_annee_de_bachelier(dto, repo)

        nouvelle_adresse = AdresseFeuilleDeNotesBuilder().build_from_repository_dto(dto)
        repo.save(nouvelle_adresse)

        if is_adresse_premiere_annee_de_bachelier_identique:
            dto_premiere_annee_de_bachelier = attr.evolve(
                dto,
                nom_cohorte=cls.__get_nom_cohorte_premiere_annee_de_bachelier_a_partir_de_nom_cohorte_bachelier(
                    dto.nom_cohorte
                )
            )
            nouvelle_adresse_premiere_annee_de_bachelier = AdresseFeuilleDeNotesBuilder().build_from_repository_dto(
                dto_premiere_annee_de_bachelier
            )
            repo.save(nouvelle_adresse_premiere_annee_de_bachelier)

        return nouvelle_adresse.entity_id

    @classmethod
    def _is_adresse_bachelier_identique_a_la_premiere_annee_de_bachelier(
            cls,
            dto: AdresseFeuilleDeNotesDTO,
            repo: IAdresseFeuilleDeNotesRepository,
    ) -> bool:
        identite_adresse_builder = AdresseFeuilleDeNotesIdentityBuilder()

        identite_adresse_bachelier = identite_adresse_builder.build_from_nom_cohorte(dto.nom_cohorte)
        identite_adresse_premiere_annee_de_bachelier = identite_adresse_builder.build_from_nom_cohorte(
            cls.__get_nom_cohorte_premiere_annee_de_bachelier_a_partir_de_nom_cohorte_bachelier(dto.nom_cohorte)
        )

        adresses = repo.search([identite_adresse_bachelier, identite_adresse_premiere_annee_de_bachelier])

        adresse_bachelier = next(
            (adresse for adresse in adresses if adresse.entity_id == identite_adresse_bachelier),
            None
        )
        adresse_premiere_annee_de_bachelier = next(
            (adresse for adresse in adresses if adresse.entity_id == identite_adresse_premiere_annee_de_bachelier),
            None
        )

        if adresse_bachelier is None and adresse_premiere_annee_de_bachelier is None:
            return True
        elif adresse_premiere_annee_de_bachelier is None:
            return True
        elif adresse_bachelier is not None:
            return adresse_bachelier.est_identique_a(adresse_premiere_annee_de_bachelier)
        return False

    @classmethod
    def __get_nom_cohorte_premiere_annee_de_bachelier_a_partir_de_nom_cohorte_bachelier(
            cls,
            nom_cohorte_bachelier: str
    ) -> str:
        return nom_cohorte_bachelier.replace('1BA', '11BA')

    @classmethod
    def _encoder_adresse_pour_autre_cohortes(
            cls,
            dto: AdresseFeuilleDeNotesDTO,
            repo: IAdresseFeuilleDeNotesRepository,
    ) -> 'IdentiteAdresseFeuilleDeNotes':
        nouvelle_adresse = AdresseFeuilleDeNotesBuilder().build_from_repository_dto(dto)
        repo.save(nouvelle_adresse)

        return nouvelle_adresse.entity_id
