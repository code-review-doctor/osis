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

from assessments.models.enums.score_sheet_address_choices import ScoreSheetAddressEntityType
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_builder import \
    AdresseFeuilleDeNotesBuilder
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_identity_builder import \
    AdresseFeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.commands import EncoderAdresseFeuilleDeNotesSpecifique, \
    EncoderAdresseEntiteCommeAdresseFeuilleDeNotes, SupprimerAdresseFeuilleDeNotesPremiereAnneeDeBachelier
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import IdentiteAdresseFeuilleDeNotes, \
    AdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.service \
    .adresse_feuille_de_note_premiere_annee_de_bachelier_est_specifique import \
    EntiteAdresseFeuilleDeNotesPremiereAnneeDeBachelierEstDifferenteDeCelleDuBachelier, \
    AdresseFeuilleDeNotesSpecifiquePremiereAnneeDeBachelierEstDifferenteDeCelleDuBachelier
from ddd.logic.encodage_des_notes.soumission.domain.service.annee_academique_addresse_feuille_de_notes import \
    AnneeAcademiqueAddresseFeuilleDeNotesDomaineService
from ddd.logic.encodage_des_notes.soumission.domain.service.entites_adresse_feuille_de_notes import \
    EntiteAdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.service.i_entites_cohorte import IEntitesCohorteTranslator
from ddd.logic.encodage_des_notes.soumission.domain.validator.validators_by_business_action import \
    EncoderAdresseFeuilleDeNotesValidatorLIst
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from ddd.logic.shared_kernel.academic_year.repository.i_academic_year import IAcademicYearRepository
from ddd.logic.shared_kernel.entite.repository.entiteucl import IEntiteUCLRepository
from osis_common.ddd import interface


class EncoderAdresseFeuilleDeNotesDomainService(interface.DomainService):
    @classmethod
    def supprimer_adresse_premiere_annee_de_bachelier(
            cls,
            cmd: SupprimerAdresseFeuilleDeNotesPremiereAnneeDeBachelier,
            repo: IAdresseFeuilleDeNotesRepository,
            periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
            academic_year_repo: 'IAcademicYearRepository'
    ) -> 'IdentiteAdresseFeuilleDeNotes':
        annee_academique = cls._get_annee_academique(periode_soumission_note_translator, academic_year_repo)

        identite_adresse = AdresseFeuilleDeNotesIdentityBuilder().build_from_nom_cohorte_and_annee_academique(
            cmd.nom_cohorte,
            annee_academique
        )

        repo.delete(identite_adresse)

        return identite_adresse

    @classmethod
    def encoder_adresse_entite_comme_adresse(
            cls,
            cmd: EncoderAdresseEntiteCommeAdresseFeuilleDeNotes,
            repo: IAdresseFeuilleDeNotesRepository,
            entite_repository: 'IEntiteUCLRepository',
            entites_cohorte_translator: 'IEntitesCohorteTranslator',
            periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
            academic_year_repo: 'IAcademicYearRepository'
    ) -> 'IdentiteAdresseFeuilleDeNotes':
        annee_academique = cls._get_annee_academique(periode_soumission_note_translator, academic_year_repo)

        EntiteAdresseFeuilleDeNotesPremiereAnneeDeBachelierEstDifferenteDeCelleDuBachelier(
        ).verifier(
            cmd,
            annee_academique,
            repo,
            entite_repository,
            entites_cohorte_translator,
            periode_soumission_note_translator,
            academic_year_repo
        )
        EncoderAdresseFeuilleDeNotesValidatorLIst(type_entite=cmd.type_entite).validate()

        entites_possibles = EntiteAdresseFeuilleDeNotes.search(
            cmd.nom_cohorte,
            entite_repository,
            entites_cohorte_translator,
            periode_soumission_note_translator,
            academic_year_repo
        )
        entite = entites_possibles.get_par_type(cmd.type_entite)

        dto = AdresseFeuilleDeNotesDTO(
            nom_cohorte=cmd.nom_cohorte,
            annee_academique=annee_academique,
            type_entite=cmd.type_entite,
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
    def encoder_adresse_specifique(
            cls,
            cmd: EncoderAdresseFeuilleDeNotesSpecifique,
            repo: IAdresseFeuilleDeNotesRepository,
            periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
            academic_year_repo: 'IAcademicYearRepository'
    ) -> 'IdentiteAdresseFeuilleDeNotes':
        annee_academique = cls._get_annee_academique(periode_soumission_note_translator, academic_year_repo)

        AdresseFeuilleDeNotesSpecifiquePremiereAnneeDeBachelierEstDifferenteDeCelleDuBachelier().verifier(
            cmd=cmd,
            annee_academique=annee_academique,
            repo=repo
        )

        EncoderAdresseFeuilleDeNotesValidatorLIst(
            type_entite=""
        ).validate()

        dto = AdresseFeuilleDeNotesDTO(
            nom_cohorte=cmd.nom_cohorte,
            annee_academique=annee_academique,
            type_entite="",
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
        nouvelle_adresse = AdresseFeuilleDeNotesBuilder().build_from_repository_dto(dto)
        repo.save(nouvelle_adresse)

        cls._supprimer_adresse_11ba_si_equivalente_a_celle_du_1ba(
            nouvelle_adresse,
            repo
        )

        return nouvelle_adresse.entity_id

    @classmethod
    def _supprimer_adresse_11ba_si_equivalente_a_celle_du_1ba(
            cls,
            adresse: 'AdresseFeuilleDeNotes',
            repo: IAdresseFeuilleDeNotesRepository
    ):
        if not ('1BA' in adresse.nom_cohorte and '11BA' not in adresse.nom_cohorte):
            return

        nom_cohorte_11BA = adresse.nom_cohorte.replace('1BA', '11BA')
        identite_adresse_11ba = AdresseFeuilleDeNotesIdentityBuilder.build_from_nom_cohorte_and_annee_academique(
            nom_cohorte_11BA,
            adresse.annee_academique
        )
        adresse_11ba = repo.get(identite_adresse_11ba)

        if adresse_11ba and adresse.est_identique_a(adresse_11ba):
            repo.delete(identite_adresse_11ba)

    @classmethod
    def _get_annee_academique(
            cls,
            periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
            academic_year_repo: 'IAcademicYearRepository'
    ) -> int:
        return AnneeAcademiqueAddresseFeuilleDeNotesDomaineService().get(
            periode_soumission_note_translator,
            academic_year_repo
        )
