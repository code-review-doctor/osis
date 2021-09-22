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
import datetime

import mock
from django.test import TestCase, override_settings

from attribution.api.serializers.effective_class_repartition import EffectiveClassRepartitionSerializer
from attribution.calendar.access_schedule_calendar import AccessScheduleCalendar
from base.business.academic_calendar import AcademicEvent
from base.models.enums.academic_calendar_type import AcademicCalendarTypes


@override_settings(
    SCHEDULE_APP_URL="https://schedule_dummy.uclouvain.be/{code}"
)
class EffectiveClassRepartitionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.class_repartition = {
            'code': "LDROI1001A",
            'title_fr': "Introduction aux droits Partie I",
            'title_en': "Introduction aux droits Partie I",
            'has_peps': False
        }

        cls.academic_event = AcademicEvent(
            id=15,
            title="Accès horaire ADE",
            authorized_target_year=2020,
            start_date=datetime.date.today() - datetime.timedelta(days=2),
            end_date=datetime.date.today() + datetime.timedelta(days=10),
            type=AcademicCalendarTypes.ACCESS_SCHEDULE_CALENDAR.name
        )

        cls.serializer = EffectiveClassRepartitionSerializer(cls.class_repartition, context={
            'access_schedule_calendar': AccessScheduleCalendar(),
            'year': cls.academic_event.authorized_target_year
        })

    def setUp(self) -> None:
        self.patcher_get_academic_events = mock.patch(
            'attribution.api.views.attribution.AccessScheduleCalendar._get_academic_events',
            new_callable=mock.PropertyMock
        )
        self.mock_get_academic_events = self.patcher_get_academic_events.start()
        self.mock_get_academic_events.return_value = [self.academic_event]
        self.addCleanup(self.patcher_get_academic_events.stop)

    def test_contains_expected_fields(self):
        expected_fields = [
            'code',
            'title_fr',
            'title_en',
            'links',
            'has_peps'
        ]
        self.assertCountEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_schedule_app_url_correctly_computed_case_calendar_opened(self):
        expected_url = "https://schedule_dummy.uclouvain.be/{code}".format(
            code=self.class_repartition.get('code')
        )
        self.assertEquals(self.serializer.data['links']['schedule'], expected_url)
