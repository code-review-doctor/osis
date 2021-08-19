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

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.encodage.builder.identite_note_etudiant_builder import NoteEtudiantIdentityBuilder
from ddd.logic.encodage_des_notes.encodage.builder.note_etudiant_builder import NoteEtudiantBuilder
from ddd.logic.encodage_des_notes.encodage.commands import EncoderNoteCommand
from ddd.logic.encodage_des_notes.encodage.domain.model.gestionnaire_parcours import GestionnaireParcours
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.shared_kernel.dtos import PeriodeEncodageNotesDTO
from osis_common.ddd import interface

NouvelleNote = str
EmailEtudiant = str


class EncoderNotesEnLot(interface.DomainService):

    @classmethod
    def execute(
            cls,
            notes_encodees: List['EncoderNoteCommand'],
            gestionnaire_parcours: 'GestionnaireParcours',
            note_etudiant_repo: 'INoteEtudiantRepository',
            periode_ouverte: 'PeriodeEncodageNotesDTO'
    ) -> List['IdentiteNoteEtudiant']:
        identites_a_modifier = [
            NoteEtudiantIdentityBuilder().build(
                note_encodee.noma,
                note_encodee.code_unite_enseignement,
                periode_ouverte.annee_concernee,
                periode_ouverte.session_concernee,
            ) for note_encodee in notes_encodees
        ]
        anciennes_notes_a_modifier = note_etudiant_repo.search(entity_ids=identites_a_modifier)

        exceptions = []
        notes_a_persister = list()
        note_etudiant_par_identite = {n.entity_id: n for n in anciennes_notes_a_modifier}

        for note_encodee in notes_encodees:
            nouvelle_valeur_note = note_encodee.note
            email_encode = note_encodee.email
            identite = NoteEtudiantIdentityBuilder().build(
                note_encodee.noma,
                note_encodee.code_unite_enseignement,
                periode_ouverte.annee_concernee,
                periode_ouverte.session_concernee,
            )
            ancienne_note_etudiant = note_etudiant_par_identite.get(identite)
            if ancienne_note_etudiant:
                try:
                    gestionnaire_parcours.verifier_gere_cohorte(ancienne_note_etudiant.nom_cohorte)
                    nouvelle_note = NoteEtudiantBuilder().build_from_ancienne_note(
                        ancienne_note=ancienne_note_etudiant,
                        email_encode=email_encode,
                        nouvelle_note=nouvelle_valeur_note,
                    )
                    notes_a_persister.append(nouvelle_note)
                except MultipleBusinessExceptions as e:
                    exceptions += list(e.exceptions)

        for note in notes_a_persister:
            note_etudiant_repo.save(note)

        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)

        return [n.entity_id for n in notes_a_persister]
