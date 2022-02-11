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
from __future__ import annotations

from typing import List
from typing import TYPE_CHECKING

import attr

from base.ddd.utils.business_validator import TwoStepsMultipleBusinessExceptionListValidator, BusinessValidator
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.preparation_programme_annuel_etudiant.domain.validator._should_au_moins_ajoute_une_unite_enseignement import \
    ShouldAuMoinsAjouterUneUniteEnseignement
from ddd.logic.preparation_programme_annuel_etudiant.domain.validator._should_unite_enseignement_pas_deja_supprimee import \
    ShouldUniteEnseignementPasDejaSupprimee

if TYPE_CHECKING:
    from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
        GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.validator.\
    _should_unite_enseignement_pas_deja_ajoutee import ShouldUniteEnseignementPasDejaAjoutee


@attr.s(frozen=True, slots=True, auto_attribs=True)
class AjouterUniteEnseignementValidatorList(TwoStepsMultipleBusinessExceptionListValidator):

    groupement_ajuste: GroupementAjusteInscriptionCours
    unites_enseignement: List[LearningUnitIdentity]

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return [
            ShouldAuMoinsAjouterUneUniteEnseignement(self.unites_enseignement)
        ]

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldUniteEnseignementPasDejaAjoutee(self.groupement_ajuste, ue)
            for ue in self.unites_enseignement
        ]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class SupprimerUniteEnseignementValidatorList(TwoStepsMultipleBusinessExceptionListValidator):

    groupement_ajuste: GroupementAjusteInscriptionCours
    unite_enseignement: LearningUnitIdentity

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldUniteEnseignementPasDejaSupprimee(self.groupement_ajuste, self.unite_enseignement)
        ]
