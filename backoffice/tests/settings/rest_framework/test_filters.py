# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from django.test import SimpleTestCase

from backoffice.settings.rest_framework.filters import MultipleColumnOrderingFilter


class TestMultipleColumnOrderingFilter(SimpleTestCase):

    def setUp(self):
        self.map_to = ('last_name', 'first_name')
        self.map_from = 'full_name'
        self.ordering_filter = MultipleColumnOrderingFilter(fields=((self.map_to, self.map_from),))

    def test_map_field_to_multiple_ordering_values(self):
        self.assertEqual(self.ordering_filter.map_multiple_ordering_values(['full_name']), list(self.map_to))

    def test_map_field_to_multiple_ordering_values_along_with_sorting_direction(self):
        self.map_to = ("-%s" % field for field in self.map_to)
        self.assertEqual(self.ordering_filter.map_multiple_ordering_values(['-full_name']), list(self.map_to))
