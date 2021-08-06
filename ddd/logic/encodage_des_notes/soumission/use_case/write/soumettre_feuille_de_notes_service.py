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
from ddd.logic.encodage_des_notes.soumission.builder.note_etudiant_identity_builder import NoteEtudiantIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.commands import SoumettreNoteCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.service.i_periode_soumission_notes import \
    IPeriodeSoumissionNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.periode_soumission_ouverte import PeriodeSoumissionOuverte
from ddd.logic.encodage_des_notes.soumission.domain.service.responsable_de_notes import ResponsableDeNotes
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository


def soumettre_note_etudiant(
        cmd: 'SoumettreNoteCommand',
        note_etudiant_repo: 'INoteEtudiantRepository',
        responsable_notes_repo: 'IResponsableDeNotesRepository',
        periode_soumission_note_translator: 'IPeriodeSoumissionNotesTranslator',
) -> 'IdentiteNoteEtudiant':
    # Given
    PeriodeSoumissionOuverte().verifier(
        periode_soumission_note_translator,
    )
    note_etudiant_identity = NoteEtudiantIdentityBuilder.build_from_command(cmd)
    note = note_etudiant_repo.get(note_etudiant_identity)

    ResponsableDeNotes().verifier(
        cmd.matricule_fgs_enseignant,
        note.code_unite_enseignement,
        note.annee,
        responsable_notes_repo
    )

    # When
    note.soumettre()

    # Then
    note_etudiant_repo.save(note)
    # Historiser (DomainService)

    return note_etudiant_identity
