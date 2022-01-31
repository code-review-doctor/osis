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

import uuid as uuid
from typing import List, Union

import attr

from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjoutee, UniteEnseignementAjouteeIdentity
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_modifiee import \
    UniteEnseignementModifiee
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_supprimee import \
    UniteEnseignementSupprimee
from ddd.logic.preparation_programme_annuel_etudiant.domain.validator.validators_by_business_action import \
    AjouterUniteEnseignementValidatorList
from education_group.ddd.domain.group import GroupIdentity
from learning_unit.ddd.domain.learning_unit_year_identity import LearningUnitYearIdentity
from osis_common.ddd import interface

CodeUniteEnseignement = str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class IdentiteGroupementAjusteInscriptionCours(interface.EntityIdentity):
    uuid: uuid.UUID


@attr.s(slots=True, auto_attribs=True)
class GroupementAjusteInscriptionCours(interface.RootEntity):
    entity_id: IdentiteGroupementAjusteInscriptionCours
    groupement_id: 'GroupIdentity'
    unites_enseignement_ajoutees: List['UniteEnseignementAjoutee']
    unites_enseignement_supprimees: List['UniteEnseignementSupprimee']
    unites_enseignement_modifiees: List['UniteEnseignementModifiee']

    @property
    def annee(self):
        return self.groupement_id.year

    def get_identites_unites_enseignement_ajoutees(self) -> List['LearningUnitIdentity']:
        return [ue.unite_enseignement_identity for ue in self.unites_enseignement_ajoutees]

    def ajouter_unites_enseignements(
            self,
            codes_unites_enseignement: List['CodeUniteEnseignement']
    ) -> None:
        unites_enseignement = [
            LearningUnitIdentityBuilder.build_from_code_and_year(code=code, year=self.annee)
            for code in codes_unites_enseignement
        ]
        AjouterUniteEnseignementValidatorList(
            groupement_ajuste=self,
            unites_enseignement=unites_enseignement,
        ).validate()
        for ue in unites_enseignement:
            self.unites_enseignement_ajoutees.append(
                UniteEnseignementAjoutee(
                    entity_id=UniteEnseignementAjouteeIdentity(uuid.uuid4()),
                    unite_enseignement_identity=ue,
                )
            )

    def retirer_unite_enseignement(self, unite_enseignement: 'LearningUnitYearIdentity'):
        raise NotImplementedError

    def ajuster_unite_enseignement(
            self,
            unite_enseignement: 'LearningUnitYearIdentity',
    ):
        raise NotImplementedError

    def annuler_action_sur_unite_enseignement(
            self,
            unite_enseignement: 'LearningUnitYearIdentity',
    ):
        # une seule action disponible à la fois
        # => retirer dans unites_enseignement_ajoutees | unites_enseignement_retirees | unites_enseignement_ajustees
        raise NotImplementedError

    def deplacer_unite_enseignement_ajoutee(
            self,
            unite_enseignement_identity: 'UniteEnseignementAjouteeIdentity',
            a_la_suite_de: Union['LearningUnitYearIdentity', 'GroupIdentity']
    ):
        raise NotImplementedError
