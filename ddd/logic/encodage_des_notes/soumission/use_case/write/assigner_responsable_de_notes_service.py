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
from ddd.logic.encodage_des_notes.soumission.builder.responsable_de_notes_builder import ResponsableDeNotesBuilder
from ddd.logic.encodage_des_notes.soumission.builder.responsable_de_notes_identity_builder import \
    ResponsableDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.commands import AssignerResponsableDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.responsable_de_notes import IdentiteResponsableDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.service.enseignant_attribue_unite_enseignement import \
    EnseignantAttribueUniteEnseignement
from ddd.logic.encodage_des_notes.shared_kernel.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository


def assigner_responsable_de_notes(
        cmd: 'AssignerResponsableDeNotesCommand',
        responsable_de_notes_repo: 'IResponsableDeNotesRepository',
        attribution_translator: 'IAttributionEnseignantTranslator'
) -> 'IdentiteResponsableDeNotes':
    # Given
    EnseignantAttribueUniteEnseignement().verifier(
        cmd.code_unite_enseignement,
        cmd.annee_unite_enseignement,
        cmd.matricule_fgs_enseignant,
        attribution_translator
    )

    # When
    responsable_actuel = responsable_de_notes_repo.get_for_unite_enseignement(
        cmd.code_unite_enseignement,
        cmd.annee_unite_enseignement
    )
    responsable_actuel.desassigner(cmd.code_unite_enseignement, cmd.annee_unite_enseignement)

    nouveau_responsable = responsable_de_notes_repo.get(ResponsableDeNotesIdentityBuilder.build_from_command(cmd)) or \
        ResponsableDeNotesBuilder().build_from_command(cmd)
    nouveau_responsable.assigner(cmd.code_unite_enseignement, cmd.annee_unite_enseignement)

    # Then
    responsable_de_notes_repo.save(responsable_actuel)
    responsable_de_notes_repo.save(nouveau_responsable)

    return nouveau_responsable.entity_id
