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
import factory
import uuid

from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours, IdentiteGroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.tests.factory.unite_enseignement_ajoutee import \
    UniteEnseignementAjouteeFactory
from education_group.ddd.domain.group import GroupIdentity


class IdentiteGroupementAjusteInscriptionCoursFactory(factory.Factory):
    class Meta:
        model = IdentiteGroupementAjusteInscriptionCours
        abstract = False

    uuid = factory.LazyFunction(uuid.uuid4)


class GroupIdentityFactory(factory.Factory):
    class Meta:
        model = GroupIdentity
        abstract = False

    code = "MAT2ECGE"
    year = 2021


class GroupementAjusteInscriptionCoursFactory(factory.Factory):
    class Meta:
        model = GroupementAjusteInscriptionCours
        abstract = False

    entity_id = factory.SubFactory(IdentiteGroupementAjusteInscriptionCoursFactory)
    groupement_id = factory.SubFactory(GroupIdentityFactory)
    programme_id = factory.SubFactory(GroupIdentityFactory, code="LECGE100B")

    unites_enseignement_ajoutees = factory.LazyFunction(list)
    unites_enseignement_supprimees = factory.LazyFunction(list)
    unites_enseignement_modifiees = factory.LazyFunction(list)

    class Params:
        ajoutees = factory.Trait(
            unites_enseignement_ajoutees=[
                UniteEnseignementAjouteeFactory(
                    unite_enseignement_identity__code='LSINF1311',
                    unite_enseignement_identity__academic_year__year=2021,
                )
            ]
        )