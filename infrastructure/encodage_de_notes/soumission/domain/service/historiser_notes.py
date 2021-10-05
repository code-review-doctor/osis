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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List

import attr
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from osis_history.utilities import add_history_entry

from base.models.person import Person
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.service.i_historiser_notes import IHistoriserNotesService
from infrastructure.encodage_de_notes.shared_kernel.service.historiser_notes import get_history_identity

TAGS = ['encodage_de_notes', 'soumission']


@attr.s(frozen=True, slots=True)
class HistoriqueNotes:
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)
    numero_session = attr.ib(type=int)
    notes = attr.ib(type=List[NoteEtudiant], factory=list)

    def get_notes_display(self) -> str:
        notes_avec_noma = [
            str(_("(Noma: %(noma)s, Score: %(score)s)") % {
                'noma': note.noma,
                'score': str(note.note)
            }) for note in self.notes
        ]
        return ','.join(notes_avec_noma)

    def get_history_identity(self) -> str:
        return get_history_identity(self.code_unite_enseignement, self.annee_academique, self.numero_session)

    def get_soumission_text(self):
        return _("The following scores %(scores_with_noma)s has been submitted") % {
            'scores_with_noma': self.get_notes_display()
        }

    def get_encodage_text(self):
        return _("The following scores %(scores_with_noma)s has been encoded") % {
            'scores_with_noma': self.get_notes_display()
        }


class HistoriserNotesService(IHistoriserNotesService):
    @classmethod
    def historiser_soumission(cls, matricule: str, notes_soumises: List['NoteEtudiant']) -> None:
        author = Person.objects.get(global_id=matricule)
        historique_notes = cls._build_historique_notes(notes_soumises)

        for historique in historique_notes:
            with translation.override('fr-be'):
                message_fr = str(historique.get_soumission_text())
            with translation.override('en'):
                message_en = str(historique.get_soumission_text())

            add_history_entry(
                historique.get_history_identity(),
                message_fr,
                message_en,
                author=author.full_name,
                tags=TAGS,
            )

    @classmethod
    def historiser_encodage(cls, matricule: str, notes_encodees: List['NoteEtudiant']) -> None:
        author = Person.objects.get(global_id=matricule)
        historique_notes = cls._build_historique_notes(notes_encodees)

        for historique in historique_notes:
            with translation.override('fr-be'):
                message_fr = str(historique.get_encodage_text())
            with translation.override('en'):
                message_en = str(historique.get_encodage_text())

            add_history_entry(
                historique.get_history_identity(),
                message_fr,
                message_en,
                author=author.full_name,
                tags=TAGS,
            )

    @classmethod
    def _build_historique_notes(cls, notes: List['NoteEtudiant']) -> List['HistoriqueNotes']:
        historique_notes = {}
        for note in notes:
            group_by_key = (note.code_unite_enseignement, note.annee, note.numero_session,)
            if not historique_notes.get(group_by_key):
                historique_notes[group_by_key] = HistoriqueNotes(
                    code_unite_enseignement=note.code_unite_enseignement,
                    annee_academique=note.annee,
                    numero_session=note.numero_session,
                    notes=[],
                )
            historique_notes[group_by_key].notes.append(note)
        return list(historique_notes.values())
