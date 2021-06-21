##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase

from attribution.models.enums import function
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from attribution.tests.factories.attribution_new import AttributionNewFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class AttributionChargeNewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory(first_name="John", last_name="Doe")
        cls.tutor = TutorFactory(person=cls.person)
        cls.attribution_new = AttributionNewFactory(tutor=cls.tutor, function=function.PROFESSOR)
        cls.attribution_charge_new_lecturing = AttributionChargeNewFactory(
            attribution=cls.attribution_new,
            allocation_charge=10
        )

    def test_str_function(self):
        self.assertEqual(self.attribution_charge_new_lecturing.__str__(), "DOE, John - PROFESSOR")
