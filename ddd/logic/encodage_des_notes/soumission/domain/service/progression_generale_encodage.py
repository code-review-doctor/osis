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

from ddd.logic.encodage_des_notes.shared_kernel.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_signaletique_etudiant import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.shared_kernel.service.progression_generale import ProgressionGeneral
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.shared_kernel.dtos import ProgressionGeneraleEncodageNotesDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository
from osis_common.ddd import interface


class ProgressionGeneraleEncodage(interface.DomainService):

    @classmethod
    def get(
            cls,
            matricule_fgs_enseignant: str,
            note_etudiant_repo: 'INoteEtudiantRepository',
            responsable_notes_repo: 'IResponsableDeNotesRepository',
            attribution_translator: 'IAttributionEnseignantTranslator',
            periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
            signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
            unite_enseignement_translator: 'IUniteEnseignementTranslator',
    ) -> 'ProgressionGeneraleEncodageNotesDTO':
        periode_soumission = periode_soumission_note_translator.get()
        annee_academique = periode_soumission.annee_concernee
        numero_session = periode_soumission.session_concernee

        notes = _search_notes(
            attribution_translator,
            note_etudiant_repo,
            matricule_fgs_enseignant,
            numero_session,
            annee_academique
        )

        return ProgressionGeneral().get(
            {note.entity_id for note in notes},
            note_etudiant_repo,
            responsable_notes_repo,
            periode_soumission,
            signaletique_etudiant_translator,
            unite_enseignement_translator
        )


def _search_notes(
        attribution_translator: 'IAttributionEnseignantTranslator',
        note_etudiant_repo: 'INoteEtudiantRepository',
        matricule_fgs_enseignant: str,
        session_concerne: int,
        annee_concerne: int
) -> List['NoteEtudiant']:
    attributions = attribution_translator.search_attributions_enseignant_par_matricule(
        annee_concerne,
        matricule_fgs_enseignant
    )
    search_criterias = [(attrib.code_unite_enseignement, annee_concerne, session_concerne) for attrib in attributions]
    return note_etudiant_repo.search_by_code_unite_enseignement_annee_session(criterias=search_criterias)
