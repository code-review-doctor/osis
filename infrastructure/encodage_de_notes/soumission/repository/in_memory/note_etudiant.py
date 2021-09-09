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
from typing import List, Set

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import NoteEtudiant, IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.soumission.dtos import DateEcheanceNoteDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository, SearchCriteria


class NoteEtudiantInMemoryRepository(InMemoryGenericRepository, INoteEtudiantRepository):
    entities = list()  # type: List[NoteEtudiant]

    @classmethod
    def search(
            cls,
            entity_ids: List['IdentiteNoteEtudiant'] = None,
            code_unite_enseignement: str = None,
            annee_academique: int = None,
            numero_session: int = None,
            **kwargs
    ) -> List['NoteEtudiant']:
        if not (entity_ids or code_unite_enseignement or annee_academique or numero_session):
            return []

        result = cls.entities
        if entity_ids:
            result = (note for note in result if note.entity_id in entity_ids)

        if code_unite_enseignement:
            result = (note for note in result if note.entity_id.code_unite_enseignement == code_unite_enseignement)

        if annee_academique:
            result = (note for note in result if note.annee == annee_academique)

        if numero_session:
            result = (note for note in result if note.numero_session == numero_session)

        return list(result)

    @classmethod
    def search_by_code_unite_enseignement_annee_session(
            cls,
            criterias: List[SearchCriteria]
    ) -> List['NoteEtudiant']:
        return [
            entity
            for entity in cls.entities
            if (entity.code_unite_enseignement, entity.annee, entity.numero_session) in criterias
        ]

    @classmethod
    def search_dates_echeances(
            cls,
            notes_identites: Set[IdentiteNoteEtudiant]
    ) -> List[DateEcheanceNoteDTO]:
        entities_sorted = sorted(cls.entities, key=lambda entity: (
            entity.code_unite_enseignement,
            entity.annee,
            entity.date_limite_de_remise.to_date(),
        ))
        return [
            DateEcheanceNoteDTO(
                code_unite_enseignement=entity.code_unite_enseignement,
                annee_unite_enseignement=entity.annee,
                numero_session=entity.numero_session,
                noma=entity.noma,
                jour=entity.date_limite_de_remise.jour,
                mois=entity.date_limite_de_remise.mois,
                annee=entity.date_limite_de_remise.annee,
                note_soumise=entity.est_soumise,
            ) for entity in entities_sorted
        ]
