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
from django.test import TestCase
from django.utils.translation import gettext_lazy as _


from assessments.forms.score_encoding import ScoreSearchForm


class ScoreSearchFormTest(TestCase):
    def setUp(self) -> None:
        self.matricule_fgs_gestionnaire = '123456789'

    def test_assert_at_least_one_criteria_must_be_filled_in(self):
        form = ScoreSearchForm(matricule_fgs_gestionnaire=self.matricule_fgs_gestionnaire, data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), [_("Please choose at least one criteria!")])
