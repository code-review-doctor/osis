# ##############################################################################
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
# ##############################################################################
from typing import Optional, List

import attr

from base.ddd.utils.business_validator import TwoStepsMultipleBusinessExceptionListValidator, BusinessValidator
from ddd.logic.admission.preparation.projet_doctoral.business_types import *
from ddd.logic.admission.preparation.projet_doctoral.domain.model._experience_precedente_recherche import \
    ChoixDoctoratDejaRealise
from ddd.logic.admission.preparation.projet_doctoral.domain.model._promoteur import PromoteurIdentity
from ddd.logic.admission.preparation.projet_doctoral.domain.model._membre_CA import MembreCAIdentity
from ddd.logic.admission.preparation.projet_doctoral.domain.validator._should_institution_dependre_doctorat_realise import \
    ShouldInstitutionDependreDoctoratRealise
from ddd.logic.admission.preparation.projet_doctoral.domain.validator._should_membre_CA_pas_deja_present_dans_groupe_de_supervision import \
    ShouldMembreCAPasDejaPresentDansGroupeDeSupervision
from ddd.logic.admission.preparation.projet_doctoral.domain.validator._should_promoteur_pas_deja_present_dans_groupe_de_supervision import \
    ShouldPromoteurPasDejaPresentDansGroupeDeSupervision
from ddd.logic.admission.preparation.projet_doctoral.domain.validator._should_type_contrat_travail_dependre_type_financement import \
    ShouldTypeContratTravailDependreTypeFinancement


@attr.s(frozen=True, slots=True)
class InitierPropositionValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    type_financement = attr.ib(type=str)
    type_contrat_travail = attr.ib(type=Optional[str], default='')
    doctorat_deja_realise = attr.ib(type=str, default=ChoixDoctoratDejaRealise.NO.name)
    institution = attr.ib(type=Optional[str], default='')

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldTypeContratTravailDependreTypeFinancement(self.type_financement, self.type_contrat_travail),
            ShouldInstitutionDependreDoctoratRealise(self.doctorat_deja_realise, self.institution),
        ]


@attr.s(frozen=True, slots=True)
class CompletionPropositionValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    type_financement = attr.ib(type=str)
    type_contrat_travail = attr.ib(type=Optional[str], default='')
    doctorat_deja_realise = attr.ib(type=str, default=ChoixDoctoratDejaRealise.NO.name)
    institution = attr.ib(type=Optional[str], default='')

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldTypeContratTravailDependreTypeFinancement(self.type_financement, self.type_contrat_travail),
            ShouldInstitutionDependreDoctoratRealise(self.doctorat_deja_realise, self.institution),
        ]


@attr.s(frozen=True, slots=True)
class SoumettrePropositionValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    proposition = attr.ib(type='Proposition')  # type: Proposition

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return []


@attr.s(frozen=True, slots=True)
class IdentifierPromoteurValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    groupe_de_supervision = attr.ib(type='GroupeDeSupervision')  # type: GroupeDeSupervision
    promoteur_id = attr.ib(type='PromoteurIdentity')  # type: PromoteurIdentity

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        membre_CA_id = MembreCAIdentity(matricule=self.promoteur_id.matricule)
        return [
            ShouldPromoteurPasDejaPresentDansGroupeDeSupervision(self.groupe_de_supervision, self.promoteur_id),
            ShouldMembreCAPasDejaPresentDansGroupeDeSupervision(self.groupe_de_supervision, membre_CA_id),
        ]


@attr.s(frozen=True, slots=True)
class IdentifierMembreCAValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    groupe_de_supervision = attr.ib(type='GroupeDeSupervision')  # type: GroupeDeSupervision
    membre_CA_id = attr.ib(type='MembreCAIdentity')  # type: MembreCAIdentity

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        promoteur_id = PromoteurIdentity(matricule=self.membre_CA_id.matricule)
        return [
            ShouldMembreCAPasDejaPresentDansGroupeDeSupervision(self.groupe_de_supervision, self.membre_CA_id),
            ShouldPromoteurPasDejaPresentDansGroupeDeSupervision(self.groupe_de_supervision, promoteur_id),
        ]
