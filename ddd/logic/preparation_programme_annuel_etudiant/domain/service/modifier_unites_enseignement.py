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
from typing import List, Union, Optional

from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.preparation_programme_annuel_etudiant.commands import ModifierUEDuGroupementCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.dtos import GroupementContenantDTO, UNITE_ENSEIGNEMENT, \
    UniteEnseignementContenueDTO, GroupementContenuDTO


class ModifierUnitesEnseignement:
    @classmethod
    def modifier_unites_enseignement(
            cls,
            cmd: 'ModifierUEDuGroupementCommand',
            groupement_contenant: 'GroupementContenantDTO',
            groupement_ajuste: 'GroupementAjusteInscriptionCours'
    ) -> None:
        for cmd_ue in cmd.unites_enseignements:
            unite_enseignement_identite = LearningUnitIdentityBuilder.build_from_code_and_year(
                code=cmd_ue.code,
                year=cmd_ue.annee
            )
            cls.__ajuster_unites_enseignement(
                groupement_ajuste,
                unite_enseignement_identite,
                bloc_initial=cls.__get_bloc_initial(groupement_contenant.elements_contenus, cmd_ue.code),
                bloc_ajuste=cmd_ue.bloc
            )

    @classmethod
    def __ajuster_unites_enseignement(
            cls,
            groupement_ajuste: 'GroupementAjusteInscriptionCours',
            unite_enseignement_identite: 'LearningUnitIdentity',
            bloc_initial: Optional[int],
            bloc_ajuste: Optional[int]
    ):
        if bloc_initial == bloc_ajuste:
            groupement_ajuste.annuler_action_sur_unite_enseignement(unite_enseignement_identite)
        else:
            groupement_ajuste.ajuster_unite_enseignement(
                unite_enseignement_identite=unite_enseignement_identite,
                bloc=bloc_ajuste
            )

    @classmethod
    def __get_bloc_initial(
            cls,
            elements: List[Union['UniteEnseignementContenueDTO', 'GroupementContenuDTO']],
            code_unite_enseignement: str
    ) -> int:
        return next(element.bloc for element in elements if element.type == UNITE_ENSEIGNEMENT
                    and element.code == code_unite_enseignement)
