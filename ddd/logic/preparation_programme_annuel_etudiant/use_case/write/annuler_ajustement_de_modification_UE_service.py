##############################################################################
#
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from ddd.logic.preparation_programme_annuel_etudiant.commands import AnnulerAjustementDeModificationCommand
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from education_group.ddd.domain.group import GroupIdentity


def annuler_ajustement_de_modification_ue(
        cmd: 'AnnulerAjustementDeModificationCommand',
        repository: 'IGroupementAjusteInscriptionCoursRepository',
) -> None:
    # GIVEN
    groupement_racine_id = GroupIdentity(
        code=cmd.code_programme,
        year=cmd.annee
    )
    groupement_id = GroupIdentity(
        code=cmd.code_groupement,
        year=cmd.annee
    )
    groupement_ajuste = repository.search_ue_ajustee_en_modification(
        programme_id=groupement_racine_id,
        groupement_id=groupement_id,
        code_unite_uuid=cmd.code_unite_enseignement_uuid
    )
    # WHEN
    repository.delete_ajustement_modification(groupement_ajuste)
