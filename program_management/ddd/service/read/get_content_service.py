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
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.node import build_title
from program_management.ddd.domain.service import identity_search
from program_management.ddd.dtos import UniteEnseignementDTO, ContenuNoeudDTO
from program_management.ddd.repositories import program_tree_version as program_tree_version_repository
from program_management.ddd.repositories.program_tree_version import _get_credits
from program_management.ddd.repositories.program_tree_version import get_verbose_title_group


def get_content_service(cmd: GetContenuGroupementCommand) -> ContenuNoeudDTO:

    tree_version_identity = identity_search.ProgramTreeVersionIdentitySearch(
    ).get_from_node_identity(
        NodeIdentity(
            code=cmd.code_programme,
            year=cmd.annee
        )
    )
    pgm_tree_version = tree_version_identity and program_tree_version_repository.ProgramTreeVersionRepository(
    ).get(tree_version_identity)

    return _build_contenu_pgm(pgm_tree_version.get_tree().get_node_by_code_and_year(code=cmd.code, year=cmd.annee))


def _build_contenu_pgm(node: 'Node', lien_parent: 'Link' = None) -> 'ContenuNoeudDTO':
    contenu = []
    for lien in node.children:
        if lien.child.is_learning_unit():
            contenu.append(
                UniteEnseignementDTO(
                    bloc=lien.block,
                    code=lien.child.code,
                    intitule_complet=lien.child.title,
                    quadrimestre=lien.child.quadrimester,
                    quadrimestre_texte=lien.child.quadrimester.value if lien.child.quadrimester else "",
                    credits_absolus=lien.child.credits,
                    volume_annuel_pm=int(lien.child.volume_total_lecturing)
                    if lien.child.volume_total_lecturing else None,
                    volume_annuel_pp=int(lien.child.volume_total_practical)
                    if lien.child.volume_total_practical else None,
                    obligatoire=lien.is_mandatory if lien else False,
                    session_derogation=lien.child.session_derogation,
                    credits_relatifs=lien.relative_credits
                )
            )
        else:
            groupement_contenu = _build_contenu_pgm(lien.child, lien_parent=lien)
            contenu.append(groupement_contenu)

    if node.is_group():
        full_title = get_verbose_title_group(node)
    else:
        full_title = build_title(node, "fr_be").lstrip(' - ')
    return ContenuNoeudDTO(
        code=node.code,
        intitule=node.full_acronym,
        remarque=node.remark_fr,
        obligatoire=lien_parent.is_mandatory if lien_parent else False,
        credits=_get_credits(lien_parent),
        intitule_complet=full_title,
        contenu_ordonne=contenu,
    )
