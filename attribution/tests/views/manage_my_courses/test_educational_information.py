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

from django.http import HttpResponseForbidden
from django.test import TestCase
from django.urls import reverse

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from attribution.views.manage_my_courses.educational_information import _fetch_achievements_by_language
from base.business.academic_calendar import AcademicEvent
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.tests.factories.academic_calendar import OpenAcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_achievement import LearningAchievementFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory
from reference.tests.factories.language import FrenchLanguageFactory, EnglishLanguageFactory


class TestTutorViewEducationalInformation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_academic_year = AcademicYearFactory(current=True)

        cls.tutor = TutorFactory()
        cls.learning_unit_year = LearningUnitYearFactory(summary_locked=False, academic_year=cls.current_academic_year)
        cls.attribution = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__learning_container_year=cls.learning_unit_year.learning_container_year,
            learning_component_year__learning_unit_year=cls.learning_unit_year,
        )
        OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name,
            data_year=cls.learning_unit_year.academic_year
        )
        cls.url = reverse('view_educational_information', args=[cls.learning_unit_year.id])

    def setUp(self):
        self.client.force_login(self.tutor.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_user_has_not_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "manage_my_courses/educational_information.html")

    def test_assert_keys_in_context(self):
        response = self.client.get(self.url)

        context = response.context
        self.assertEqual(context["learning_unit_year"], self.learning_unit_year)
        self.assertTrue("teaching_materials" in context)
        self.assertFalse(context["cms_labels_translated"])
        self.assertTrue(context["can_edit_information"])
        self.assertFalse(context["can_edit_summary_locked_field"])
        self.assertIsInstance(context["submission_dates"], AcademicEvent)

        # Verify URL for tutor [==> Specific redirection]
        self.assertEqual(context['create_teaching_material_urlname'], 'tutor_teaching_material_create')
        self.assertEqual(context['update_teaching_material_urlname'], 'tutor_teaching_material_edit')
        self.assertEqual(context['delete_teaching_material_urlname'], 'tutor_teaching_material_delete')
        self.assertEqual(context['update_mobility_modality_urlname'], 'tutor_mobility_modality_update')


class TestFetchAchievementsByLanguage(TestCase):
    @classmethod
    def setUpTestData(cls):
        fr = FrenchLanguageFactory()
        en = EnglishLanguageFactory()
        cls.learning_unit_year = LearningUnitYearFactory()
        cls.achievement_fr = LearningAchievementFactory(language=fr, learning_unit_year=cls.learning_unit_year)
        cls.achievement_en = LearningAchievementFactory(language=en, learning_unit_year=cls.learning_unit_year)

    def test_return_an_iterable_of_fr_and_en_achievements(self):
        result = _fetch_achievements_by_language(self.learning_unit_year)
        self.assertListEqual(
            list(result),
            list(zip([self.achievement_fr], [self.achievement_en]))
        )
