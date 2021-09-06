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
from ddd.logic.encodage_des_notes.soumission.commands import EncoderAdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import AdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    AdressePremiereAnneeDeBachelierIdentiqueAuBachlierException
from ddd.logic.encodage_des_notes.soumission.repository.i_adresse_feuille_de_notes import \
    IAdresseFeuilleDeNotesRepository
from osis_common.ddd import interface


class AdresseFeuilleDeNotesPremiereAnneeDeBachelierEstSpecifique(interface.DomainService):
    @classmethod
    def verifier(
            cls,
            cmd: EncoderAdresseFeuilleDeNotes,
            repo: IAdresseFeuilleDeNotesRepository
    ) -> None:
        if "11BA" not in cmd.nom_cohorte:
            return

        nom_cohorte_bachelier = cmd.nom_cohorte.replace("11BA", "1BA")
        identite_adresse_bachelier = AdresseFeuilleDeNotesIdentityBuilder().build_from_nom_cohorte(
            nom_cohorte_bachelier
        )
        adresse_bachelier = repo.get(identite_adresse_bachelier)

        if cls._is_adresse_bachelier_identique_a_la_nouvelle_adresse_du_11ba(adresse_bachelier, cmd):
            raise AdressePremiereAnneeDeBachelierIdentiqueAuBachlierException()

    @classmethod
    def _is_adresse_bachelier_identique_a_la_nouvelle_adresse_du_11ba(
            cls,
            adresse_bachelier: AdresseFeuilleDeNotes,
            cmd: EncoderAdresseFeuilleDeNotes
    ) -> bool:
        return adresse_bachelier.sigle_entite == cmd.entite and cmd.entite
