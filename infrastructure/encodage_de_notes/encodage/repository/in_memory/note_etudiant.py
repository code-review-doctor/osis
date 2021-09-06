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
from typing import List, Optional, Set

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from base.models.enums.exam_enrollment_justification_type import JustificationTypes
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import NoteEtudiant, IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository


class NoteEtudiantInMemoryRepository(InMemoryGenericRepository, INoteEtudiantRepository):
    entities = list()  # type: List[NoteEtudiant]

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteNoteEtudiant']] = None,
            noms_cohortes: List[str] = None,
            nomas: List[str] = None,
            note_manquante: bool = False,
            justification: JustificationTypes = None,
            **kwargs
    ) -> List['NoteEtudiant']:
        if not (entity_ids or noms_cohortes or nomas or note_manquante or justification):
            return []

        result = cls.entities
        if entity_ids:
            result = (note for note in result if note.entity_id in entity_ids)

        if noms_cohortes:
            result = (note for note in result if note.nom_cohorte in noms_cohortes)

        if nomas:
            result = (note for note in result if note.noma in nomas)

        if note_manquante:
            result = (note for note in result if note.is_manquant)

        if justification:
            result = (note for note in result if note.note.value == justification)

        return list(result)

    @classmethod
    def search_notes_identites(
            cls,
            noms_cohortes: List[str] = None,
            annee_academique: int = None,
            numero_session: int = None,
            nomas: List[str] = None,
            code_unite_enseignement: str = None,
            enseignant: str = None,
            note_manquante: bool = False,
            **kwargs
    ) -> Set['IdentiteNoteEtudiant']:
        if not (noms_cohortes or annee_academique or numero_session or nomas
                or note_manquante or code_unite_enseignement):
            return set()

        result = cls.search(noms_cohortes=noms_cohortes, nomas=nomas, note_manquante=note_manquante)
        if code_unite_enseignement:
            result = (note for note in result if note.entity_id.code_unite_enseignement in code_unite_enseignement)
        if annee_academique:
            result = (note for note in result if note.entity_id.annee_academique == annee_academique)
        if numero_session:
            result = (note for note in result if note.entity_id.numero_session == numero_session)
        return {note.entity_id for note in result}
