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
from ddd.logic.preparation_programme_annuel_etudiant.domain.builder.groupement_ajuste_inscription_cours_identity_builder import \
    GroupementAjusteInscriptionCoursIdentityBuilder
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    IdentiteGroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository


def ajouter_UE_au_programme(
        cmd: 'AjouterUEAuProgrammeCommand',
        repository: 'IGroupementAjusteInscriptionCoursRepository',
) -> 'IdentiteGroupementAjusteInscriptionCours':
    # GIVEN
    identite_groupement_ajuste = GroupementAjusteInscriptionCoursIdentityBuilder.build_from_command(cmd)
    groupement_ajuste = repository.get(
        entity_id=identite_groupement_ajuste
    )

    # WHEN
    for cmd_ue in cmd.unites_enseignements:
        groupement_ajuste.ajouter_unite_enseignement(
            unite_enseignement=cmd_ue.code,
        )

    # THEN
    repository.save(groupement_ajuste)
    return groupement_ajuste.entity_id
