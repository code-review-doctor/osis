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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import string

import factory.fuzzy

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory


class AttributionClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "attribution.AttributionClass"

    external_id = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    attribution_charge = factory.SubFactory(
        AttributionChargeNewFactory,
        learning_component_year=factory.SelfAttribute('..learning_class_year.learning_component_year')
    )
    learning_class_year = factory.SubFactory(LearningClassYearFactory)
    allocation_charge = 0
