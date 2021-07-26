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
from ddd.logic.encodage_des_notes.soumission.builder.feuille_de_notes_identity_builder import \
    FeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.commands import EncoderFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import IdentiteFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.service.encoder_feuille_de_notes import EncoderFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.service.enseignant_attribue_unite_enseignement import \
    EnseignantAttribueUniteEnseignement
from ddd.logic.encodage_des_notes.soumission.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.i_periode_soumission_notes import \
    IPeriodeSoumissionNotesTranslator
from ddd.logic.encodage_des_notes.soumission.domain.service.periode_soumission_ouverte import \
    PeriodeSoumissionOuverte
from ddd.logic.encodage_des_notes.soumission.repository.i_feuille_de_notes import IFeuilleDeNotesRepository


def encoder_feuille_de_notes(
        cmd: 'EncoderFeuilleDeNotesCommand',
        feuille_de_note_repo: 'IFeuilleDeNotesRepository',
        periode_soumission_note_translator: 'IPeriodeSoumissionNotesTranslator',
        attribution_translator: 'IAttributionEnseignantTranslator'
) -> 'IdentiteFeuilleDeNotes':
    # Given
    PeriodeSoumissionOuverte().verifier(
        cmd.annee_unite_enseignement,
        cmd.numero_session,
        periode_soumission_note_translator,
    )
    EnseignantAttribueUniteEnseignement().verifier(cmd, attribution_translator)
    feuille_de_note_identity = FeuilleDeNotesIdentityBuilder.build_from_command(cmd)
    feuille_de_notes = feuille_de_note_repo.get(feuille_de_note_identity)

    # When
    EncoderFeuilleDeNotes().encoder(cmd, feuille_de_notes)

    # Then
    feuille_de_note_repo.save(feuille_de_notes)
    # TODO :: Historiser (DomainService) ?

    return feuille_de_notes.entity_id
