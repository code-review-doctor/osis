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
from collections import OrderedDict
from typing import List, Tuple, Dict

from ddd.logic.encodage_des_notes.encodage.builder.identite_note_etudiant_builder import NoteEtudiantIdentityBuilder
from ddd.logic.encodage_des_notes.encodage.commands import EncoderNotesCommand
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.encodage.domain.service.gestionnaire_parcours import GestionnaireParcours
from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.service.i_periode_encodage_notes import IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.periode_encodage_ouverte import PeriodeEncodageOuverte

NouvelleNote = str
EmailEtudiant = str


# TODO :: unit tests
def encoder_notes(
        cmd: 'EncoderNotesCommand',
        note_etudiant_repo: 'INoteEtudiantRepository',
        periode_encodage_note_translator: 'IPeriodeEncodageNotesTranslator',
        cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
) -> List['IdentiteNoteEtudiant']:
    # Given
    PeriodeEncodageOuverte().verifier(periode_encodage_note_translator)
    GestionnaireParcours().verifier(cmd.matricule_fgs_gestionnaire, cohortes_gestionnaire_translator)
    periode_ouverte = periode_encodage_note_translator.get()
    note_par_identite = __associer_nouvelle_note_a_son_identite(cmd, periode_ouverte)
    identites_notes_a_modifier = list(note_par_identite.keys())
    notes_a_modifier = note_etudiant_repo.search(entity_ids=identites_notes_a_modifier)
    GestionnaireParcours().verifier_cohortes_gerees(
        matricule_gestionnaire=cmd.matricule_fgs_gestionnaire,
        cohortes_a_verifier={note.nom_cohorte for note in notes_a_modifier},
        cohortes_gestionnaire_translator=cohortes_gestionnaire_translator,
    )

    # TODO : capturer dans EncoderNotesEnLotDomainService?
    for note_etudiant in notes_a_modifier:

        # When
        nouvelle_note = note_par_identite[note_etudiant.entity_id][0]
        email = note_par_identite[note_etudiant.entity_id][1]
        note_etudiant.encoder(nouvelle_note, email)

        # Then
        # TODO :: performance : implémenter un repo.save_in_bulk ?
        note_etudiant_repo.save(note_etudiant)

    return identites_notes_a_modifier


def __associer_nouvelle_note_a_son_identite(
        cmd: 'EncoderNotesCommand',
        periode_ouverte,
) -> Dict[IdentiteNoteEtudiant, Tuple[NouvelleNote, EmailEtudiant]]:
    notes = OrderedDict()
    for note_cmd in cmd.notes_encodees:
        identity = NoteEtudiantIdentityBuilder().build(
            note_cmd.noma,
            note_cmd.code_unite_enseignement,
            periode_ouverte.annee_concernee,
            periode_ouverte.session_concernee,
        )
        notes[identity] = (note_cmd.note, note_cmd.email)
    return notes
