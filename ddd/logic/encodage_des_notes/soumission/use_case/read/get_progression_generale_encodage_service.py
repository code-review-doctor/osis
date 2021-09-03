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
from ddd.logic.encodage_des_notes.shared_kernel.dtos import ProgressionGeneraleEncodageNotesDTO
from ddd.logic.encodage_des_notes.shared_kernel.domain.service import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service import \
    ISignaletiqueEtudiantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_unite_enseignement import IUniteEnseignementTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.periode_encodage_ouverte import PeriodeEncodageOuverte
from ddd.logic.encodage_des_notes.soumission.commands import GetProgressionGeneraleCommand
from ddd.logic.encodage_des_notes.soumission.domain.service.progression_generale_encodage import \
    ProgressionGeneraleEncodage
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository


def get_progression_generale(
        cmd: 'GetProgressionGeneraleCommand',
        note_etudiant_repo: 'INoteEtudiantRepository',
        responsable_notes_repo: 'IResponsableDeNotesRepository',
        periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
        signaletique_etudiant_translator: 'ISignaletiqueEtudiantTranslator',
        attribution_translator: 'IAttributionEnseignantTranslator',
        unite_enseignement_translator: 'IUniteEnseignementTranslator',
) -> 'ProgressionGeneraleEncodageNotesDTO':
    # Given
    PeriodeEncodageOuverte().verifier(periode_soumission_note_translator)

    # When
    progression_dto = ProgressionGeneraleEncodage().get(
        matricule_fgs_enseignant=cmd.matricule_fgs_enseignant,
        note_etudiant_repo=note_etudiant_repo,
        responsable_notes_repo=responsable_notes_repo,
        attribution_translator=attribution_translator,
        periode_soumission_note_translator=periode_soumission_note_translator,
        signaletique_etudiant_translator=signaletique_etudiant_translator,
        unite_enseignement_translator=unite_enseignement_translator,
    )

    # Then
    return progression_dto
