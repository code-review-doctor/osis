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
from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.preparation_programme_annuel_etudiant.commands import ModifierUEDuGroupementCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours


class ModifierUnitesEnseignement:
    @classmethod
    def modifier_unites_enseignement(
            cls,
            cmd: 'ModifierUEDuGroupementCommand',
            groupement_ajuste: 'GroupementAjusteInscriptionCours'
    ) -> None:
        for cmd_ue in cmd.unites_enseignements:
            learning_unit_identity = LearningUnitIdentityBuilder.build_from_code_and_year(
                code=cmd_ue.code,
                year=cmd_ue.annee
            )
            groupement_ajuste.ajuster_unite_enseignement(
                unite_enseignement=learning_unit_identity,
                bloc=cmd_ue.bloc
            )
