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

from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.tests.factories.cohort_year import CohortYearFactory
from base.tests.factories.offer_year_calendar import OfferYearCalendarFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from ddd.logic.encodage_des_notes.soumission.dtos import DateDTO
from infrastructure.encodage_de_notes.soumission.domain.service.deliberation import DeliberationTranslator


class DeliberationTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.annee = 2020
        cls.numero_session = 2
        cls.translator = DeliberationTranslator()

    def test_should_renvoyer_aucun_resultat(self):
        result = self.translator.search(self.annee, self.numero_session, {'DROI2M'})
        self.assertEqual(result, set())

    def test_should_renvoyer_date_deliberation(self):
        nom_cohorte = 'DROI1BA'
        off_calendar = OfferYearCalendarFactory(
            academic_calendar__reference=AcademicCalendarTypes.DELIBERATION.name,
            education_group_year__academic_year__year=self.annee,
            education_group_year__acronym=nom_cohorte,
        )
        SessionExamCalendarFactory(academic_calendar=off_calendar.academic_calendar, number_session=self.numero_session)
        result = self.translator.search(self.annee, self.numero_session, {nom_cohorte})
        dto = list(result)[0]
        self.assertEqual(dto.nom_cohorte, nom_cohorte)
        start_date = off_calendar.start_date
        self.assertEqual(dto.date, DateDTO(jour=start_date.day, mois=start_date.month, annee=start_date.year))

    def test_should_renvoyer_date_deliberation_cohorte_11BA(self):
        off_calendar = OfferYearCalendarFactory(
            academic_calendar__reference=AcademicCalendarTypes.DELIBERATION.name,
            education_group_year__academic_year__year=self.annee,
            education_group_year__acronym="DROI1BA",
        )
        SessionExamCalendarFactory(academic_calendar=off_calendar.academic_calendar, number_session=self.numero_session)
        CohortYearFactory(education_group_year=off_calendar.education_group_year)  # 11BA
        result = self.translator.search(self.annee, self.numero_session, {'DROI11BA'})
        dto = list(result)[0]
        self.assertEqual(dto.nom_cohorte, 'DROI11BA')
        start_date = off_calendar.start_date
        self.assertNotEqual(dto.date, DateDTO(jour=start_date.day, mois=start_date.month, annee=start_date.year))
        # TODO :: assertion sur date de délibé du 11BA
