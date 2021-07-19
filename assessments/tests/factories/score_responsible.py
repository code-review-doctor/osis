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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import factory

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from attribution.tests.factories.attribution_class import AttributionClassFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory


class ScoreResponsibleFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'assessments.ScoreResponsible'

    learning_unit_year = factory.SubFactory(LearningUnitYearFactory)
    attribution_charge = factory.SubFactory(
        AttributionChargeNewFactory,
        learning_component_year__learning_unit_year=factory.LazyAttribute(
            lambda component: component.factory_parent.factory_parent.learning_unit_year
        )
    )
    attribution_class = None


class ScoreResponsibleOfClassFactory(ScoreResponsibleFactory):
    attribution_class = factory.SubFactory(
        AttributionClassFactory,
        learning_class_year__learning_component_year__learning_unit_year=factory.LazyAttribute(
            lambda class_year: class_year.factory_parent.factory_parent.factory_parent.learning_unit_year
        )
    )
    attribution_charge = None
