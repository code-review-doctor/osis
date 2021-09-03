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

from ddd.logic.encodage_des_notes.encodage.builder.gestionnaire_parcours_builder import GestionnaireParcoursBuilder
from ddd.logic.encodage_des_notes.encodage.commands import EncoderNotesCommand
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.encodage.domain.service.encoder_notes_en_lot import EncoderNotesEnLot
from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.domain.service import IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.periode_encodage_ouverte import PeriodeEncodageOuverte

NouvelleNote = str
EmailEtudiant = str


def encoder_notes(
        cmd: 'EncoderNotesCommand',
        note_etudiant_repo: 'INoteEtudiantRepository',
        periode_encodage_note_translator: 'IPeriodeEncodageNotesTranslator',
        cohortes_gestionnaire_translator: 'ICohortesDuGestionnaire',
) -> List['IdentiteNoteEtudiant']:
    # Given
    PeriodeEncodageOuverte().verifier(periode_encodage_note_translator)
    gestionnaire_parcours = GestionnaireParcoursBuilder().get(
        matricule_gestionnaire=cmd.matricule_fgs_gestionnaire,
        cohortes_gestionnaire_translator=cohortes_gestionnaire_translator,
    )
    periode_ouverte = periode_encodage_note_translator.get()

    # WHEN
    notes = EncoderNotesEnLot().execute(cmd.notes_encodees, gestionnaire_parcours, note_etudiant_repo, periode_ouverte)

    return notes
