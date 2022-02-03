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
import uuid
from typing import Union

from ddd.logic.preparation_programme_annuel_etudiant.commands import AjouterUEAuProgrammeCommand, \
    SupprimerUEDuProgrammeCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    IdentiteGroupementAjusteInscriptionCours, GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from education_group.ddd.domain.group import GroupIdentity
from osis_common.ddd import interface


class GroupementAjusteInscriptionCoursBuilder(interface.RootEntityBuilder):
    @classmethod
    def build_from_add_command(
            cls,
            cmd: Union['AjouterUEAuProgrammeCommand'],
            repository: 'IGroupementAjusteInscriptionCoursRepository'
    ) -> 'GroupementAjusteInscriptionCours':
        return cls._build_from_group_identity(
            group_identity=GroupIdentity(
                code=cmd.ajouter_dans,
                year=cmd.annee,
            ),
            repository=repository
        )

    @classmethod
    def build_from_delete_command(
            cls,
            cmd: Union['SupprimerUEDuProgrammeCommand'],
            repository: 'IGroupementAjusteInscriptionCoursRepository'
    ) -> 'GroupementAjusteInscriptionCours':
        return cls._build_from_group_identity(
            group_identity=GroupIdentity(
                code=cmd.retirer_de,
                year=cmd.annee,
            ),
            repository=repository
        )

    @classmethod
    def _build_from_group_identity(
            cls,
            group_identity: 'GroupIdentity',
            repository: 'IGroupementAjusteInscriptionCoursRepository'
    ):
        groupements_ajustes = repository.search(groupement_id=group_identity)
        if groupements_ajustes:
            return groupements_ajustes[0]
        return GroupementAjusteInscriptionCours(
            entity_id=IdentiteGroupementAjusteInscriptionCours(uuid=uuid.uuid4()),
            groupement_id=group_identity,
            unites_enseignement_ajoutees=[],
            unites_enseignement_supprimees=[],
            unites_enseignement_modifiees=[],
        )
