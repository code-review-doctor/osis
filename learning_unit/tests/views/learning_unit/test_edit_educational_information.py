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

from django.contrib import messages
from django.http.response import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.business.learning_unit import CMS_LABEL_PEDAGOGY_FR_ONLY
from base.models.enums import entity_type
from base.models.enums import organization_type
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import FacultyManagerForUEFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from base.tests.factories.utils.get_messages import get_messages_from_response
from cms.enums import entity_name
from cms.tests.factories.translated_text import LearningUnitYearTranslatedTextFactory


class LearningUnitPedagogyEditTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = datetime.datetime.now()
        cls.academic_year = create_current_academic_year()
        cls.previous_academic_year = AcademicYearFactory(year=cls.academic_year.year - 1)
        cls.next_academic_year = AcademicYearFactory(year=cls.academic_year.year + 1)
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
        cls.learning_unit_year = LearningUnitYearFactory(
            acronym="LBIR1100",
            academic_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__acronym="LBIR1100",
            learning_container_year__requirement_entity=cls.requirement_entity_version.entity
        )
        cls.url = reverse('learning_unit_pedagogy_edit', kwargs={'learning_unit_year_id': cls.learning_unit_year.pk})
        cls.faculty_person = FacultyManagerForUEFactory('can_access_learningunit', 'can_edit_learningunit_pedagogy')

    def setUp(self):
        self.cms = LearningUnitYearTranslatedTextFactory(
            reference=self.learning_unit_year.pk,
            language='fr-be',
            text='Some random text',
            text_label__entity=entity_name.LEARNING_UNIT_YEAR,
            text_label__label='bibliography',
        )
        self.client.force_login(self.faculty_person.user)

    def test_learning_unit_pedagogy_edit(self):
        response = self.client.get(self.url, data={'label': 'bibliography', 'language': 'fr-be'})

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'learning_unit/blocks/modal/modal_pedagogy_edit.html')
        self.assertEqual(response.context["cms_label_pedagogy_fr_only"], CMS_LABEL_PEDAGOGY_FR_ONLY)
        self.assertEqual(response.context["label_name"], 'bibliography')

    def test_learning_unit_pedagogy_edit_post(self):
        msg = self._post_learning_unit_pedagogy()
        self.assertEqual(msg[0].get('message'), "{}".format(_("The learning unit has been updated (without report).")))
        self.assertEqual(msg[0].get('level'), messages.SUCCESS)

    def test_learning_unit_pedagogy_edit_post_with_postponement(self):
        LearningUnitYearFactory(
            acronym="LBIR1100",
            academic_year=self.next_academic_year,
            learning_container_year__academic_year=self.next_academic_year,
            learning_container_year__acronym="LBIR1100",
            learning_container_year__requirement_entity=self.requirement_entity_version.entity,
            learning_unit=self.learning_unit_year.learning_unit
        )
        msg = self._post_learning_unit_pedagogy()
        expected_message = "{} {}.".format(
            _("The learning unit has been updated"),
            _("and postponed until %(year)s") % {
                "year": self.next_academic_year
            }
        )
        self.assertEqual(msg[0].get('message'), expected_message)
        self.assertEqual(msg[0].get('level'), messages.SUCCESS)

    def test_learning_unit_pedagogy_edit_post_with_postponement_and_proposal(self):
        LearningUnitYearFactory(
            acronym="LBIR1100",
            academic_year=self.next_academic_year,
            learning_container_year__academic_year=self.next_academic_year,
            learning_container_year__acronym="LBIR1100",
            learning_container_year__requirement_entity=self.requirement_entity_version.entity,
            learning_unit=self.learning_unit_year.learning_unit
        )
        proposal = ProposalLearningUnitFactory(learning_unit_year=self.learning_unit_year)
        msg = self._post_learning_unit_pedagogy()
        expected_message = "{}. {}.".format(
            _("The learning unit has been updated"),
            _("The learning unit is in proposal, the report from %(proposal_year)s will be done at consolidation") % {
                'proposal_year': proposal.learning_unit_year.academic_year
            }
        )
        self.assertEqual(msg[0].get('message'), expected_message)
        self.assertEqual(msg[0].get('level'), messages.SUCCESS)

    def test_learning_unit_pedagogy_edit_post_with_proposal(self):
        proposal = ProposalLearningUnitFactory(learning_unit_year=self.learning_unit_year)
        msg = self._post_learning_unit_pedagogy()
        expected_message = "{}. {}.".format(
            _("The learning unit has been updated"),
            _("The learning unit is in proposal, the report from %(proposal_year)s will be done at consolidation") % {
                'proposal_year': proposal.learning_unit_year.academic_year
            }
        )
        self.assertEqual(msg[0].get('message'), expected_message)
        self.assertEqual(msg[0].get('level'), messages.SUCCESS)

    def test_learning_unit_pedagogy_edit_post_with_proposal_previous_year(self):
        previous_luy = LearningUnitYearFactory(
            acronym="LBIR1100",
            academic_year=self.previous_academic_year,
            learning_container_year__academic_year=self.previous_academic_year,
            learning_container_year__acronym="LBIR1100",
            learning_container_year__requirement_entity=self.requirement_entity_version.entity,
            learning_unit=self.learning_unit_year.learning_unit
        )
        ProposalLearningUnitFactory(learning_unit_year=previous_luy)
        msg = self._post_learning_unit_pedagogy()
        expected_message = "{}".format(_("The learning unit has been updated (without report)."))
        self.assertEqual(msg[0].get('message'), expected_message)
        self.assertEqual(msg[0].get('level'), messages.SUCCESS)

    def test_learning_unit_pedagogy_edit_post_with_proposal_next_year(self):
        next_luy = LearningUnitYearFactory(
            acronym="LBIR1100",
            academic_year=self.next_academic_year,
            learning_container_year__academic_year=self.next_academic_year,
            learning_container_year__acronym="LBIR1100",
            learning_container_year__requirement_entity=self.requirement_entity_version.entity,
            learning_unit=self.learning_unit_year.learning_unit
        )
        proposal = ProposalLearningUnitFactory(learning_unit_year=next_luy)
        msg = self._post_learning_unit_pedagogy()
        expected_message = "{} ({}).".format(
            _("The learning unit has been updated"),
            _("the report has not been done from %(proposal_year)s because the LU is in proposal") % {
                'proposal_year': proposal.learning_unit_year.academic_year
            }
        )
        self.assertEqual(msg[0].get('message'), expected_message)
        self.assertEqual(msg[0].get('level'), messages.SUCCESS)

    def _post_learning_unit_pedagogy(self):
        response = self.client.post(self.url, data={
            'cms_id': self.cms.pk,
            'trans_text': 'test',
            'learning_unit_year': self.learning_unit_year
        })
        self.assertEqual(response.status_code, HttpResponse.status_code)
        msg = get_messages_from_response(response)
        return msg
