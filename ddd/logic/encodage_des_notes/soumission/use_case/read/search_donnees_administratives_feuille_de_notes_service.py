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
from typing import List

from ddd.logic.encodage_des_notes.soumission.commands import SearchAdressesFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.service.donnees_administratives import DonneesAdministratives
from ddd.logic.encodage_des_notes.soumission.domain.service.i_contact_feuille_de_notes import \
    IContactFeuilleDeNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_deliberation import IDeliberationTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_periode_soumission_notes import \
    IPeriodeSoumissionNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import DonneesAdministrativesFeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository


def search_donnees_administratives_feuille_de_notes(
        cmd: 'SearchAdressesFeuilleDeNotesCommand',
        periode_soumission_note_translator: 'IPeriodeSoumissionNotesTranslator',
        contact_feuille_notes_translator: 'IContactFeuilleDeNotesTranslator',
        signaletique_personne_translator: 'ISignaletiquePersonneTranslator',
        inscr_exam_translator: 'IInscriptionExamenTranslator',
        responsable_notes_repo: 'IResponsableDeNotesRepository',
        deliberation_translator: 'IDeliberationTranslator',
) -> List['DonneesAdministrativesFeuilleDeNotesDTO']:
    return DonneesAdministratives().search(
        codes_unites_enseignement=cmd.codes_unite_enseignement,
        periode_soumission_note_translator=periode_soumission_note_translator,
        contact_feuille_notes_translator=contact_feuille_notes_translator,
        signaletique_personne_translator=signaletique_personne_translator,
        inscr_exam_translator=inscr_exam_translator,
        responsable_notes_repo=responsable_notes_repo,
        deliberation_translator=deliberation_translator,
    )
