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
import datetime

import mock
from django.contrib import messages
from django.db.models.query import QuerySet
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse, HttpResponseNotAllowed
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from attribution.views.manage_my_courses import _fetch_achievements_by_language
from base.business.academic_calendar import AcademicEvent
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.tests.factories.academic_calendar import AcademicCalendarFactory, OpenAcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_achievement import LearningAchievementFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.teaching_material import TeachingMaterialFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory
from base.tests.factories.utils.get_messages import get_messages_from_response
from reference.tests.factories.language import FrenchLanguageFactory, EnglishLanguageFactory


class ListMyAttributionsSummaryEditableTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()

        cls.current_academic_year = AcademicYearFactory(current=True)
        cls.ac_year_in_past = AcademicYearFactory.produce_in_past(cls.current_academic_year.year)
        cls.ac_year_in_future = AcademicYearFactory.produce_in_future(cls.current_academic_year.year)

        # Create multiple attribution in different academic years
        for ac_year in cls.ac_year_in_past + [cls.current_academic_year] + cls.ac_year_in_future:
            learning_unit_year = LearningUnitYearFactory(summary_locked=False, academic_year=ac_year)
            AttributionChargeNewFactory(
                attribution__tutor=cls.tutor,
                attribution__learning_container_year=learning_unit_year.learning_container_year,
                learning_component_year__learning_unit_year=learning_unit_year,
            )
        cls.url = reverse('list_my_attributions_summary_editable')

    def setUp(self):
        self.summary_course_calendar = OpenAcademicCalendarFactory(
            data_year=self.current_academic_year,
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name
        )
        self.summary_course_force_majeure_calendar = OpenAcademicCalendarFactory(
            data_year=self.current_academic_year,
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION_FORCE_MAJEURE.name
        )

        self.client.force_login(self.tutor.person.user)

    def test_list_my_attributions_summary_editable_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_list_my_attributions_summary_editable_user_not_tutor(self):
        person_not_tutor = PersonFactory()
        self.client.force_login(person_not_tutor.user)

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_list_my_attributions_summary_editable_assert_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "manage_my_courses/list_my_courses_summary_editable.html")

    def test_list_my_attributions_summary_editable_assert_context_keys(self):
        response = self.client.get(self.url)

        self.assertIsInstance(response.context['learning_unit_years'], QuerySet)
        self.assertIsInstance(response.context['summary_edition_academic_event'], AcademicEvent)
        self.assertEqual(
            response.context['summary_edition_academic_event'].start_date,
            self.summary_course_calendar.start_date
        )
        self.assertEqual(
            response.context['summary_edition_academic_event'].end_date,
            self.summary_course_calendar.end_date
        )

        self.assertIsInstance(response.context['force_majeure_academic_event'], AcademicEvent)
        self.assertEqual(
            response.context['force_majeure_academic_event'].start_date,
            self.summary_course_force_majeure_calendar.start_date
        )
        self.assertEqual(
            response.context['force_majeure_academic_event'].end_date,
            self.summary_course_force_majeure_calendar.end_date
        )

    def test_list_my_attributions_summary_editable_after_period(self):
        self.summary_course_calendar.start_date = datetime.date.today() - datetime.timedelta(weeks=52)
        self.summary_course_calendar.end_date = datetime.date.today() - datetime.timedelta(weeks=48)
        self.summary_course_calendar.save()

        next_calendar = AcademicCalendarFactory(
            start_date=datetime.date.today() + datetime.timedelta(weeks=48),
            end_date=datetime.date.today() + datetime.timedelta(weeks=52),
            data_year=self.ac_year_in_future[1],
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name
        )
        response = self.client.get(self.url)

        msg = get_messages_from_response(response)
        self.assertEqual(
            msg[0].get('message'),
            _('For the academic year %(data_year)s, the summary edition period ended on %(end_date)s.') % {
                "data_year": self.summary_course_calendar.data_year,
                "end_date": self.summary_course_calendar.end_date.strftime('%d/%m/%Y'),
            }
        )
        self.assertEqual(msg[0].get('level'), messages.INFO)
        self.assertEqual(
            msg[1].get('message'),
            _('For the academic year %(data_year)s, the summary edition period will open on %(start_date)s.') % {
                "data_year": next_calendar.data_year,
                "start_date": next_calendar.start_date.strftime('%d/%m/%Y'),
            }
        )
        self.assertEqual(msg[1].get('level'), messages.INFO)

    def test_list_my_attributions_force_majeure_editable_assert_warning_message_displayed(self):
        response = self.client.get(self.url)

        msg = get_messages_from_response(response)
        self.assertEqual(
            msg[0].get('message'),
            _("Force majeure case : Some fields of the description fiche can be edited from %(start_date)s to "
              "%(end_date)s.") % {
                "start_date":
                    self.summary_course_force_majeure_calendar.start_date.strftime('%d/%m/%Y'),
                "end_date":
                    self.summary_course_force_majeure_calendar.end_date.strftime('%d/%m/%Y'),
            }
        )
        self.assertEqual(msg[0].get('level'), messages.WARNING)


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


class TestTutorEditEducationalInformation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.academic_year = AcademicYearFactory(current=True)

        cls.learning_unit_year = LearningUnitYearFactory(academic_year=cls.academic_year, summary_locked=False)
        cls.attribution = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__learning_container_year=cls.learning_unit_year.learning_container_year,
            learning_component_year__learning_unit_year=cls.learning_unit_year,
        )
        cls.url = reverse("tutor_edit_educational_information", args=[cls.learning_unit_year.id])

    def setUp(self):
        self.calendar_row = OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name,
            data_year=self.learning_unit_year.academic_year
        )
        self.client.force_login(self.tutor.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_user_has_not_permission(self):
        self.client.force_login(PersonFactory().user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_summary_course_submission_calendar_is_closed(self):
        self.calendar_row.start_date = datetime.date.today() - datetime.timedelta(days=3)
        self.calendar_row.end_date = datetime.date.today() - datetime.timedelta(days=1)
        self.calendar_row.save()

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    @mock.patch('attribution.views.manage_my_courses.edit_learning_unit_pedagogy', return_value=HttpResponse())
    def test_assert_call_edit_learning_unit_pedagogy_method(self, mock_edit_learning_unit_pedagogy):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_edit_learning_unit_pedagogy.called)


class TestTutorEditForceMajeurEducationalInformation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.academic_year = AcademicYearFactory(current=True)

        cls.learning_unit_year = LearningUnitYearFactory(academic_year=cls.academic_year, summary_locked=False)
        cls.attribution = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__learning_container_year=cls.learning_unit_year.learning_container_year,
            learning_component_year__learning_unit_year=cls.learning_unit_year,
        )
        cls.url = reverse("tutor_edit_educational_information_force_majeure", args=[cls.learning_unit_year.id])

    def setUp(self):
        self.calendar_row = OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION_FORCE_MAJEURE.name,
            data_year=self.learning_unit_year.academic_year
        )
        self.client.force_login(self.tutor.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_user_has_not_permission(self):
        self.client.force_login(PersonFactory().user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_summary_course_submission_force_majeure_calendar_is_closed(self):
        self.calendar_row.start_date = datetime.date.today() - datetime.timedelta(days=3)
        self.calendar_row.end_date = datetime.date.today() - datetime.timedelta(days=1)
        self.calendar_row.save()

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    @mock.patch('attribution.views.manage_my_courses.edit_learning_unit_pedagogy', return_value=HttpResponse())
    def test_assert_get_http_call_edit_learning_unit_pedagogy_method(self, mock_edit_learning_unit_pedagogy):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_edit_learning_unit_pedagogy.called)

    @mock.patch('attribution.views.manage_my_courses.post_method_edit_force_majeure_pedagogy',
                return_value=HttpResponse())
    def test_assert_post_http_call_edit_learning_unit_pedagogy_method(self, mock_post_learning_unit_pedagogy):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_post_learning_unit_pedagogy.called)


class TestTutorCreateTeachingMaterial(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.academic_year = AcademicYearFactory(current=True)

        cls.learning_unit_year = LearningUnitYearFactory(academic_year=cls.academic_year, summary_locked=False)
        cls.attribution = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__learning_container_year=cls.learning_unit_year.learning_container_year,
            learning_component_year__learning_unit_year=cls.learning_unit_year,
        )
        cls.url = reverse("tutor_teaching_material_create", args=[cls.learning_unit_year.id])

    def setUp(self):
        self.calendar_row = OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name,
            data_year=self.learning_unit_year.academic_year
        )
        self.client.force_login(self.tutor.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_user_has_not_permission(self):
        self.client.force_login(PersonFactory().user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_summary_course_submission_calendar_is_closed(self):
        self.calendar_row.start_date = datetime.date.today() - datetime.timedelta(days=3)
        self.calendar_row.end_date = datetime.date.today() - datetime.timedelta(days=1)
        self.calendar_row.save()

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_assert_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertTemplateUsed(response, "method_not_allowed.html")
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @mock.patch('attribution.views.manage_my_courses.teaching_material.create_view', return_value=HttpResponse())
    def test_assert_get_http_call_teachning_material_create_view(self, mock_teachning_material_create_view):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_create_view.called)

    @mock.patch('attribution.views.manage_my_courses.teaching_material.create_view', return_value=HttpResponse())
    def test_assert_post_http_call_teachning_material_create_view(self, mock_teachning_material_create_view):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_create_view.called)


class TestTutorUpdateTeachingMaterial(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.academic_year = AcademicYearFactory(current=True)

        cls.learning_unit_year = LearningUnitYearFactory(academic_year=cls.academic_year, summary_locked=False)
        cls.teaching_material = TeachingMaterialFactory(learning_unit_year=cls.learning_unit_year)
        cls.attribution = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__learning_container_year=cls.learning_unit_year.learning_container_year,
            learning_component_year__learning_unit_year=cls.learning_unit_year,
        )
        cls.url = reverse('tutor_teaching_material_edit', kwargs={
            'learning_unit_year_id': cls.learning_unit_year.pk,
            'teaching_material_id': cls.teaching_material.pk
        })

    def setUp(self):
        self.calendar_row = OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name,
            data_year=self.learning_unit_year.academic_year
        )
        self.client.force_login(self.tutor.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_user_has_not_permission(self):
        self.client.force_login(PersonFactory().user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_summary_course_submission_calendar_is_closed(self):
        self.calendar_row.start_date = datetime.date.today() - datetime.timedelta(days=3)
        self.calendar_row.end_date = datetime.date.today() - datetime.timedelta(days=1)
        self.calendar_row.save()

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_assert_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertTemplateUsed(response, "method_not_allowed.html")
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @mock.patch('attribution.views.manage_my_courses.teaching_material.update_view', return_value=HttpResponse())
    def test_assert_get_http_call_teachning_material_update_view(self, mock_teachning_material_update_view):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_update_view.called)

    @mock.patch('attribution.views.manage_my_courses.teaching_material.update_view', return_value=HttpResponse())
    def test_assert_post_http_call_teachning_material_update_view(self, mock_teachning_material_update_view):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_update_view.called)


class TestTutorDeleteTeachingMaterial(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.academic_year = AcademicYearFactory(current=True)

        cls.learning_unit_year = LearningUnitYearFactory(academic_year=cls.academic_year, summary_locked=False)
        cls.teaching_material = TeachingMaterialFactory(learning_unit_year=cls.learning_unit_year)
        cls.attribution = AttributionChargeNewFactory(
            attribution__tutor=cls.tutor,
            attribution__learning_container_year=cls.learning_unit_year.learning_container_year,
            learning_component_year__learning_unit_year=cls.learning_unit_year,
        )
        cls.url = reverse('tutor_teaching_material_delete', kwargs={
            'learning_unit_year_id': cls.learning_unit_year.pk,
            'teaching_material_id': cls.teaching_material.pk
        })

    def setUp(self):
        self.calendar_row = OpenAcademicCalendarFactory(
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name,
            data_year=self.learning_unit_year.academic_year
        )
        self.client.force_login(self.tutor.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_user_has_not_permission(self):
        self.client.force_login(PersonFactory().user)
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_summary_course_submission_calendar_is_closed(self):
        self.calendar_row.start_date = datetime.date.today() - datetime.timedelta(days=3)
        self.calendar_row.end_date = datetime.date.today() - datetime.timedelta(days=1)
        self.calendar_row.save()

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_assert_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertTemplateUsed(response, "method_not_allowed.html")
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @mock.patch('attribution.views.manage_my_courses.teaching_material.delete_view', return_value=HttpResponse())
    def test_assert_get_http_call_teachning_material_delete_view(self, mock_teachning_material_delete_view):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_delete_view.called)

    @mock.patch('attribution.views.manage_my_courses.teaching_material.delete_view', return_value=HttpResponse())
    def test_assert_post_http_call_teachning_material_delete_view(self, mock_teachning_material_delete_view):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_teachning_material_delete_view.called)
