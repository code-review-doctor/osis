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

from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.periode_encodage_ouverte import PeriodeEncodageOuverte
from ddd.logic.encodage_des_notes.soumission.commands import SoumettreNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.service.i_notifier_soumission_notes import INotifierSoumissionNotes
from ddd.logic.encodage_des_notes.soumission.domain.service.responsable_de_notes import ResponsableDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.service.soumettre_notes_en_lot import SoumettreNotesEnLot
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository


def soumettre_notes_etudiant(
        cmd: 'SoumettreNotesCommand',
        note_etudiant_repo: 'INoteEtudiantRepository',
        responsable_notes_repo: 'IResponsableDeNotesRepository',
        periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
        notification_service: 'INotifierSoumissionNotes',
        translator: 'IAttributionEnseignantTranslator',
        signaletique_repo: 'ISignaletiquePersonneTranslator',
        signaletique_etudiant_repo: 'ISignaletiqueEtudiantTranslator',
) -> List['IdentiteNoteEtudiant']:
    # Given
    PeriodeEncodageOuverte().verifier(periode_soumission_note_translator)

    ResponsableDeNotes().verifier(
        cmd.matricule_fgs_enseignant,
        cmd.code_unite_enseignement,
        cmd.annee_unite_enseignement,
        responsable_notes_repo
    )

    # When
    notes_soumises = SoumettreNotesEnLot().soumettre(cmd, note_etudiant_repo)

    # Then

    notification_service.notifier(
        notes_soumises,
        note_etudiant_repo,
        translator,
        signaletique_repo,
        signaletique_etudiant_repo,
    )

    return notes_soumises
