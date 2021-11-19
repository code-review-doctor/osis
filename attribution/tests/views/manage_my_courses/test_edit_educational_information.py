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
from django.db.models import Prefetch
from django.http import HttpResponseForbidden, HttpResponse
from django.test import TestCase
from django.urls import reverse

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.business.learning_unit import CMS_LABEL_PEDAGOGY_FR_ONLY
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.models.person import get_user_interface_language
from base.tests.factories.academic_calendar import OpenAcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from base.views.learning_units.common import get_text_label_translated
from cms.models.text_label import TextLabel
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from reference.models.language import find_language_in_settings


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

    def test_assert_context(self):
        text_label = TextLabelFactory()
        ttl = TranslatedTextLabelFactory(text_label=text_label)
        text_label_from_qs = TextLabel.objects.prefetch_related(
            Prefetch('translatedtextlabel_set', to_attr="translated_text_labels")
        ).get()
        url = self.url + '?language={}&label={}'.format(
            ttl.language, text_label.label
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context['cms_label_pedagogy_fr_only'], CMS_LABEL_PEDAGOGY_FR_ONLY)
        self.assertEqual(response.context['label_name'], text_label.label)
        self.assertEqual(response.context['language_translated'], find_language_in_settings(ttl.language))
        self.assertEqual(
            response.context['text_label_translated'],
            get_text_label_translated(text_label_from_qs, get_user_interface_language(self.tutor.person.user))
        )


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
        cls.text_label = TextLabelFactory()
        cls.ttl = TranslatedTextLabelFactory(text_label=cls.text_label)
        cls.text_label_from_qs = TextLabel.objects.prefetch_related(
            Prefetch('translatedtextlabel_set', to_attr="translated_text_labels")
        ).get()

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

    def test_assert_context(self):
        url = self.url + '?language={}&label={}'.format(
            self.ttl.language, self.text_label.label
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context['cms_label_pedagogy_fr_only'], CMS_LABEL_PEDAGOGY_FR_ONLY)
        self.assertEqual(response.context['label_name'], self.text_label.label)
        self.assertEqual(response.context['language_translated'], find_language_in_settings(self.ttl.language))
        self.assertEqual(
            response.context['text_label_translated'],
            get_text_label_translated(self.text_label_from_qs, get_user_interface_language(self.tutor.person.user))
        )

    @mock.patch('base.forms.learning_unit_pedagogy.LearningUnitPedagogyEditForm.save')
    def test_assert_post_save_form_without_postpone(self, mock_save):
        url = self.url + '?language={}&label={}'.format(
            self.ttl.language, self.text_label.label
        )
        text = TranslatedTextFactory(text_label=self.text_label)
        response = self.client.post(url, data={'cms_id': text.id, 'trans_text': 'TEST'})

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_save.called)
        mock_save.assert_called_with(postpone=False)
