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

from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.service.i_notifier_soumission_notes import INotifierSoumissionNotes
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository


class InMemoryNotifierSoumissionNotes(INotifierSoumissionNotes):
    identites_notes_soumises = []

    @classmethod
    def notifier(
            cls,
            identites_notes_soumises: List['IdentiteNoteEtudiant'],
            note_etudiant_repo: 'INoteEtudiantRepository',
            attribution_enseignant_translator: 'IAttributionEnseignantTranslator',
            signaletique_personne_translator: 'ISignaletiquePersonneTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
    ) -> None:
        cls.identites_notes_soumises.append(identites_notes_soumises)
