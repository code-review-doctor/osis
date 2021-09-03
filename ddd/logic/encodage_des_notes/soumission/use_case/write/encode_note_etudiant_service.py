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
from ddd.logic.encodage_des_notes.shared_kernel.domain.service import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.periode_encodage_ouverte import \
    PeriodeEncodageOuverte
from ddd.logic.encodage_des_notes.soumission.builder.note_etudiant_identity_builder import NoteEtudiantIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.commands import EncoderNoteCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.service.enseignant_attribue_unite_enseignement import \
    EnseignantAttribueUniteEnseignement
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository


def encoder_note_etudiant(
        cmd: 'EncoderNoteCommand',
        note_etudiant_repo: 'INoteEtudiantRepository',
        periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
        attribution_translator: 'IAttributionEnseignantTranslator'
) -> 'NoteEtudiant':
    # Given
    PeriodeEncodageOuverte().verifier(periode_soumission_note_translator)
    EnseignantAttribueUniteEnseignement().verifier(
        cmd.code_unite_enseignement,
        cmd.annee_unite_enseignement,
        cmd.matricule_fgs_enseignant,
        attribution_translator
    )
    note_etudiant_identity = NoteEtudiantIdentityBuilder.build_from_command(cmd)
    note_etudiant = note_etudiant_repo.get(note_etudiant_identity)

    # When
    note_etudiant.encoder(cmd.email_etudiant, cmd.note)

    # Then
    note_etudiant_repo.save(note_etudiant)
    # TODO :: Historiser (DomainService) ?

    return note_etudiant.entity_id
