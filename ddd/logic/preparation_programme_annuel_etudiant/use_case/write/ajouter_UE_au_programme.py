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
from ddd.logic.preparation_programme_annuel_etudiant.commands import AjouterUEAuProgrammeCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.builder.programme_inscription_cours_identity_builder import \
    ProgrammeInscriptionCoursIdentityBuilder
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.programme_inscription_cours import \
    ProgrammeInscriptionCoursIdentity
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_programme_inscription_cours import \
    IProgrammeInscriptionCoursRepository


def ajouter_UE_au_programme(
        cmd: 'AjouterUEAuProgrammeCommand',
        programme_inscription_cours_repository: 'IProgrammeInscriptionCoursRepository',
) -> 'ProgrammeInscriptionCoursIdentity':
    # GIVEN
    programme_inscription_cours_identity = ProgrammeInscriptionCoursIdentityBuilder.build_from_command(cmd)
    programme_inscription_cours = programme_inscription_cours_repository.get(
        entity_id=programme_inscription_cours_identity
    )

    # WHEN
    for cmd_ue in cmd.unites_enseignements:
        programme_inscription_cours.ajouter_unite_enseignement(
            unite_enseignement=cmd_ue.code,
            a_inclure_dans=cmd.a_inclure_dans
        )

    # THEN
    return programme_inscription_cours_identity
