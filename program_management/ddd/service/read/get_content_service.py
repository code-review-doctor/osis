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
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ContenuGroupementDTO
from program_management.ddd.domain import exception
from program_management.ddd.dtos import UniteEnseignementDTO
from ddd.logic.preparation_programme_annuel_etudiant.dtos import GroupementDTO
from program_management.ddd.repositories import program_tree_version as program_tree_version_repository
from program_management.ddd.repositories.program_tree_version import _build_contenu
from program_management.ddd.repositories.program_tree_version import get_verbose_title_group


def get_content_service(cmd: GetContenuGroupementCommand) -> ContenuGroupementDTO:
    try:
        pgm_tree_version = program_tree_version_repository.ProgramTreeVersionRepository().search(
            code=cmd.code_formation,
            year=cmd.annee
        )[0]
        return _build_contenu(pgm_tree_version.get_tree().get_node_by_code_and_year(code=cmd.code, year=cmd.annee))

    except exception.ProgramTreeVersionNotFoundException:
        return None


def _build_contenu(node: 'Node', lien_parent: 'Link' = None) -> 'ContenuGroupementDTO':
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
                    volume_annuel_pm=lien.child.volume_total_lecturing,
                    volume_annuel_pp=lien.child.volume_total_practical,
                    obligatoire=lien.is_mandatory if lien else False,
                    session_derogation='',
                    credits_relatifs=lien.relative_credits
                )
            )
        else:
            groupement_contenu = _build_contenu(lien.child, lien_parent=lien)
            contenu.append(groupement_contenu)

    return ContenuGroupementDTO(
        groupement_contenant=GroupementDTO(
            intitule=node.title,
            obligatoire=lien_parent.is_mandatory if lien_parent else False,
            intitule_complet=get_verbose_title_group(node),
            chemin_acces=''
        ),
        contenu=contenu,
    )
