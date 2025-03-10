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
from io import BytesIO
from unittest.mock import patch

from django.http import HttpResponseNotAllowed
from django.http.response import HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from openpyxl import load_workbook

from base.business.learning_units.xls_generator import generate_xls_teaching_material
from base.forms.learning_unit.search.educational_information import LearningUnitDescriptionFicheFilter
from base.models.enums import entity_type
from base.models.enums import organization_type
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.models.enums.learning_unit_year_subtypes import FULL
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import FacultyManagerForUEFactory
from base.tests.factories.teaching_material import TeachingMaterialFactory
from base.tests.factories.user import UserFactory
from base.views.learning_units.search.common import SearchTypes
from cms.enums.entity_name import LEARNING_UNIT_YEAR
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from learning_unit.tests.factories.faculty_manager import FacultyManagerFactory


class LearningUnitPedagogyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = datetime.datetime.now()

        cls.academic_year = AcademicYearFactory(current=True)
        cls.old_academic_year = AcademicYearFactory(year=cls.academic_year.year - 1)
        cls.next_academic_year = AcademicYearFactory(year=cls.academic_year.year + 1)
        AcademicCalendarFactory(
            data_year=cls.old_academic_year,
            start_date=now - datetime.timedelta(days=5),
            end_date=now + datetime.timedelta(days=15),
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name
        )

        cls.requirement_entity_version = EntityVersionFactory(
            entity__organization__type=organization_type.MAIN,
            start_date=now,
            end_date=datetime.datetime(now.year + 1, 9, 15),
            entity_type=entity_type.INSTITUTE
        )
        cls.learning_unit_year = LearningUnitYearFactory(
            acronym="LBIR1100",
            academic_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__acronym="LBIR1100",
            learning_container_year__requirement_entity=cls.requirement_entity_version.entity
        )
        cls.url = reverse('learning_units_summary')
        cls.faculty_manager = FacultyManagerFactory(entity=cls.requirement_entity_version.entity, person__french=True)
        TranslatedTextLabelFactory(text_label__label='resume')

    def setUp(self):
        self.client.force_login(self.faculty_manager.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_user_has_no_right_to_access_summary_learning_unit(self):
        user_with_no_rights = UserFactory()
        self.client.force_login(user_with_no_rights)

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_learning_units_summary_list_filter_academic_year(self):
        response = self.client.get(self.url, data={'academic_year__year': self.learning_unit_year.academic_year.year})

        self.assertTemplateUsed(response, 'learning_unit/search/description_fiche.html')
        self.assertTrue(response.context['is_faculty_manager'])
        self.assertEqual(response.context['search_type'], SearchTypes.SUMMARY_LIST.value)
        self.assertEqual(response.context['learning_units_count'], 1)

        self.assertEqual(response.context['object_list'].first(), self.learning_unit_year)

    def test_learning_units_summary_list_filter_on_requirement_entity(self):
        now = datetime.datetime.now()
        another_requirement_entity_version = EntityVersionFactory(
            entity__organization__type=organization_type.MAIN,
            start_date=now,
            end_date=datetime.datetime(now.year + 1, 9, 15),
            entity_type=entity_type.SCHOOL,
            parent=self.requirement_entity_version.entity
        )
        LearningUnitYearFactory(
            acronym="LDROI1500",
            academic_year=self.academic_year,
            learning_container_year__academic_year=self.academic_year,
            learning_container_year__acronym="LDROI1500",
            learning_container_year__requirement_entity=another_requirement_entity_version.entity
        )

        # Without ent. sub
        response = self.client.get(
            self.url,
            data={
                'academic_year__year': self.learning_unit_year.academic_year.year,
                'requirement_entity': self.requirement_entity_version.acronym,
                'with_entity_subordinated': False
            }
        )
        self.assertEqual(response.context['learning_units_count'], 1)
        self.assertEqual(response.context['object_list'].first(), self.learning_unit_year)

        # With ent. sub
        response = self.client.get(
            self.url,
            data={
                'academic_year__year': self.learning_unit_year.academic_year.year,
                'requirement_entity': self.requirement_entity_version.acronym,
                'with_entity_subordinated': True
            }
        )
        self.assertEqual(response.context['learning_units_count'], 2)

    def test_learning_unit_pedagogy_read_with_learning_unit_year(self):
        url = reverse("learning_unit_pedagogy", args=[self.learning_unit_year.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue('cms_labels_translated' in response.context.keys())

    def test_learning_unit_pedagogy_read_with_code_and_year(self):
        url = reverse("learning_unit_pedagogy", args=[
            self.learning_unit_year.acronym,
            self.learning_unit_year.academic_year.year
        ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue('cms_labels_translated' in response.context.keys())


class LearningUnitPedagogyExportXLSTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = datetime.datetime.now()
        cls.academic_years = AcademicYearFactory.produce(number_past=5, number_future=5)

        cls.academic_year = cls.academic_years[5]
        cls.old_academic_year = cls.academic_years[4]
        cls.next_academic_year = cls.academic_years[5]
        cls.previous_academic_year = cls.academic_years[4]
        AcademicCalendarFactory(
            data_year=cls.previous_academic_year,
            start_date=now - datetime.timedelta(days=5),
            end_date=now + datetime.timedelta(days=15),
            reference=AcademicCalendarTypes.SUMMARY_COURSE_SUBMISSION.name
        )

        cls.requirement_entity_version = EntityVersionFactory(
            entity__organization__type=organization_type.MAIN,
            start_date=now,
            end_date=datetime.datetime(now.year + 1, 9, 15),
            entity_type=entity_type.INSTITUTE
        )

        cls.url = reverse('learning_units_summary')
        cls.faculty_person = FacultyManagerForUEFactory('can_access_learningunit', 'can_edit_learningunit_pedagogy')
        # Generate data for XLS export
        cls.learning_unit_year_with_mandatory_teaching_materials = LearningUnitYearFactory(
            acronym="LBIR1100",
            academic_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__acronym="LBIR1100",
            learning_container_year__requirement_entity=cls.requirement_entity_version.entity
        )
        TeachingMaterialFactory(
            learning_unit_year=cls.learning_unit_year_with_mandatory_teaching_materials,
            title="Magic wand",
            mandatory=True,
        )
        TeachingMaterialFactory(
            learning_unit_year=cls.learning_unit_year_with_mandatory_teaching_materials,
            title="Broomsticks",
            mandatory=False,
        )

        cls.learning_unit_year_without_mandatory_teaching_materials = LearningUnitYearFactory(
            acronym="LDROI1600",
            academic_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__acronym="LDROI1600",
            learning_container_year__requirement_entity=cls.requirement_entity_version.entity
        )
        TeachingMaterialFactory(
            learning_unit_year=cls.learning_unit_year_without_mandatory_teaching_materials,
            title="cauldron",
            mandatory=False,
        )

    def setUp(self):
        self.client.force_login(self.faculty_person.user)

    def test_learning_units_summary_list_by_client_xls(self):
        TranslatedTextFactory(
            text_label=TextLabelFactory(label='bibliography'),
            entity=LEARNING_UNIT_YEAR,
            text="<ul><li>Test</li></ul>",
            reference=self.learning_unit_year_with_mandatory_teaching_materials.pk,
            language='fr-be'
        )
        TranslatedTextFactory(
            text_label=TextLabelFactory(label='online_resources'),
            entity=LEARNING_UNIT_YEAR,
            text="<a href='test_url'>TestURL</a>",
            reference=self.learning_unit_year_with_mandatory_teaching_materials.pk,
            language='fr-be'
        )
        TranslatedTextFactory(
            text_label=TextLabelFactory(label='online_resources'),
            entity=LEARNING_UNIT_YEAR,
            text="<a href='test_url'>TestURL EN</a>",
            reference=self.learning_unit_year_with_mandatory_teaching_materials.pk,
            language='en'
        )

        response = self.client.get(self.url, data={
            'academic_year__year': self.academic_year.year,
            'xls_status': 'xls_teaching_material'
        })

        # The server returned the xls file
        self.assertEqual(response.status_code, HttpResponse.status_code)
        wb = load_workbook(BytesIO(response.content), read_only=True)

        sheet = wb.active
        data = sheet['A1': 'G3']

        # Check the first row content
        titles = next(data)
        title_values = list(t.value for t in titles)
        self.assertEqual(title_values, [
            str(_('code')).title(),
            str(_('Title')),
            str(_('Req. Entity')).title(),
            str(_('bibliography')).title(),
            str(_('teaching materials')).title(),
            str("{} - Fr-Be".format(_('online resources'))).title(),
            str("{} - En".format(_('online resources'))).title(),
        ])

        # Check data from the luy
        first_luy = next(data)
        first_luy_values = list(t.value for t in first_luy)
        self.assertEqual(first_luy_values, [
            self.learning_unit_year_with_mandatory_teaching_materials.acronym,
            self.learning_unit_year_with_mandatory_teaching_materials.complete_title,
            str(self.learning_unit_year_with_mandatory_teaching_materials.requirement_entity),
            "Test\n",
            "Magic wand",
            "TestURL - [test_url] \n",
            "TestURL EN - [test_url] \n"
        ])

        # The second luy has no mandatory teaching material
        with self.assertRaises(StopIteration):
            next(data)

    def test_learning_units_summary_list_by_client_xls_empty(self):

        form_data = {
            'acronym': self.learning_unit_year_without_mandatory_teaching_materials.acronym,
            'academic_year__year': self.academic_year.year,
            'xls_status': 'xls_teaching_material'
        }

        service_course_filter = LearningUnitDescriptionFicheFilter(form_data)
        self.assertTrue(service_course_filter.is_valid())

        response = generate_xls_teaching_material(self.faculty_person.user, service_course_filter.qs)

        self.assertEqual(response.status_code, HttpResponse.status_code)


class LearningUnitPedagogySummaryLockedTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_academic_year = create_current_academic_year()
        cls.faculty_manager = FacultyManagerFactory()
        cls.learning_unit_year = LearningUnitYearFactory(
            academic_year=cls.current_academic_year,
            learning_container_year__academic_year=cls.current_academic_year,
            subtype=FULL
        )
        cls.url = reverse('learning_unit_pedagogy_toggle_summary_locked',
                          kwargs={'learning_unit_year_id': cls.learning_unit_year.pk})

    def setUp(self):
        self.client.force_login(self.faculty_manager.person.user)

    def test_toggle_summary_locked_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_toggle_summary_locked_case_method_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    def test_toggle_summary_locked_case_cannot_edit_summary_locked(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    @patch('base.views.learning_units.pedagogy.update.display_success_messages')
    def test_toggle_summary_locked_case_success(self, mock_diplay_success_message):
        self.learning_unit_year.summary_locked = True
        self.learning_unit_year.save()
        requirement_entity = self.learning_unit_year.learning_container_year.requirement_entity
        faculty_manager = FacultyManagerFactory(entity=requirement_entity)
        self.client.force_login(faculty_manager.person.user)
        response = self.client.post(self.url, follow=False)

        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        self.assertTrue(mock_diplay_success_message.called)
        expected_redirection = reverse("learning_unit_pedagogy",
                                       kwargs={'learning_unit_year_id': self.learning_unit_year.pk})
        self.assertRedirects(response, expected_redirection)
        self.learning_unit_year.refresh_from_db()
        self.assertFalse(self.learning_unit_year.summary_locked)
