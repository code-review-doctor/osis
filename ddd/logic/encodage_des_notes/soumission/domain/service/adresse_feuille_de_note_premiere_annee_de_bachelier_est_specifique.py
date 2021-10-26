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
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_identity_builder import \
    AdresseFeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.commands import EncoderAdresseEntiteCommeAdresseFeuilleDeNotes, \
    EncoderAdresseFeuilleDeNotesSpecifique
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import AdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    EntiteAdressePremiereAnneeDeBachelierIdentiqueAuBachlierException, \
    AdresseSpecifiquePremiereAnneeDeBachelierIdentiqueAuBachlierException
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from osis_common.ddd import interface


class EntiteAdresseFeuilleDeNotesPremiereAnneeDeBachelierEstDifferenteDeCelleDuBachelier(interface.DomainService):
    @classmethod
    def verifier(
            cls,
            cmd: EncoderAdresseEntiteCommeAdresseFeuilleDeNotes,
            annee_academique: int,
            repo: IAdresseFeuilleDeNotesRepository
    ) -> None:
        if "11BA" not in cmd.nom_cohorte:
            return

        nom_cohorte_bachelier = cmd.nom_cohorte.replace("11BA", "1BA")
        identite_adresse_bachelier = AdresseFeuilleDeNotesIdentityBuilder().build_from_nom_cohorte_and_annee_academique(
            nom_cohorte_bachelier,
            annee_academique
        )
        adresse_bachelier = repo.get(identite_adresse_bachelier)

        if cls._is_entite_adresse_bachelier_identique_a_celle_de_la_premiere_annee_de_bachelier(adresse_bachelier, cmd):
            raise EntiteAdressePremiereAnneeDeBachelierIdentiqueAuBachlierException()

    @classmethod
    def _is_entite_adresse_bachelier_identique_a_celle_de_la_premiere_annee_de_bachelier(
            cls,
            adresse_bachelier: AdresseFeuilleDeNotes,
            cmd: EncoderAdresseEntiteCommeAdresseFeuilleDeNotes
    ) -> bool:
        return cmd.type_entite and adresse_bachelier.type_entite and adresse_bachelier.type_entite.name == \
               cmd.type_entite


class AdresseFeuilleDeNotesSpecifiquePremiereAnneeDeBachelierEstDifferenteDeCelleDuBachelier(interface.DomainService):
    @classmethod
    def verifier(
            cls,
            cmd: EncoderAdresseFeuilleDeNotesSpecifique,
            annee_academique: int,
            repo: IAdresseFeuilleDeNotesRepository
    ) -> None:
        if "11BA" not in cmd.nom_cohorte:
            return

        nom_cohorte_bachelier = cmd.nom_cohorte.replace("11BA", "1BA")
        identite_adresse_bachelier = AdresseFeuilleDeNotesIdentityBuilder().build_from_nom_cohorte_and_annee_academique(
            nom_cohorte_bachelier,
            annee_academique
        )
        adresse_bachelier = repo.get(identite_adresse_bachelier)

        if cls._is_adresse_specifique_identique_a_celle_de_la_premiere_annee_de_bachelier(adresse_bachelier, cmd):
            raise AdresseSpecifiquePremiereAnneeDeBachelierIdentiqueAuBachlierException()

    @classmethod
    def _is_adresse_specifique_identique_a_celle_de_la_premiere_annee_de_bachelier(
            cls,
            adresse_bachelier: AdresseFeuilleDeNotes,
            cmd: EncoderAdresseFeuilleDeNotesSpecifique
    ) -> bool:
        return cmd.fax == adresse_bachelier.fax and cmd.pays == adresse_bachelier.pays and \
            cmd.ville == adresse_bachelier.ville and cmd.email == adresse_bachelier.email and \
            cmd.destinataire == adresse_bachelier.destinataire and \
            cmd.telephone == adresse_bachelier.telephone and cmd.code_postal == adresse_bachelier.code_postal and\
            cmd.rue_numero == adresse_bachelier.rue_numero
