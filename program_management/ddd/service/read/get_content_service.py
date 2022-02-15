#############################################################################
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand
from ddd.logic.program_management.builder.contenu_noeud_dto_builder import ContenuNoeudDTOBuilder
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.service import identity_search
from program_management.ddd.dtos import ContenuNoeudDTO
from program_management.ddd.repositories import program_tree_version as program_tree_version_repository


def get_content_service(cmd: GetContenuGroupementCommand) -> ContenuNoeudDTO:

    tree_version_identity = identity_search.ProgramTreeVersionIdentitySearch(
    ).get_from_node_identity(
        NodeIdentity(
            code=cmd.code_programme,
            year=cmd.annee
        )
    )
    pgm_tree_version = program_tree_version_repository.ProgramTreeVersionRepository(
    ).get(tree_version_identity)
    return ContenuNoeudDTOBuilder.get(
        pgm_tree_version.get_tree().get_node_by_code_and_year(code=cmd.code, year=cmd.annee)
    )
