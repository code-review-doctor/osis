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
import uuid

import factory

from ddd.logic.learning_unit.tests.factory.learning_unit import LearningUnitIdentityFactory
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjoutee, UniteEnseignementAjouteeIdentity


class UniteEnseignementAjouteeIdentityFactory(factory.Factory):
    class Meta:
        model = UniteEnseignementAjouteeIdentity
        abstract = False

    uuid = factory.LazyFunction(uuid.uuid4)


class UniteEnseignementAjouteeFactory(factory.Factory):
    class Meta:
        model = UniteEnseignementAjoutee
        abstract = False

    entity_id = factory.SubFactory(UniteEnseignementAjouteeIdentityFactory)
    unite_enseignement_identity = factory.SubFactory(LearningUnitIdentityFactory)
    a_la_suite_de = None
