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
import uuid
from decimal import Decimal

from django.test import TestCase


from base.tests.factories.learning_container_year import LearningContainerYearFactory
from ddd.logic.application.domain.model.applicant import ApplicantIdentity
from ddd.logic.application.domain.model.application import Application, ApplicationIdentity
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from infrastructure.application.serializer.application import ApplicationSerializer


class ApplicationSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_container_year = LearningContainerYearFactory(
            external_id="osis.learning_container_year_428750_2017",
            academic_year__year=2017,
            acronym='LDROI1200',
        )

    def setUp(self) -> None:
        self.application = Application(
            entity_id=ApplicationIdentity(uuid=uuid.uuid4()),
            applicant_id=ApplicantIdentity(global_id="123456789"),
            vacant_course_id=VacantCourseIdentity(
                academic_year=AcademicYearIdentityBuilder.build_from_year(2017),
                code='LDROI1200'
            ),
            lecturing_volume=Decimal(5),
            practical_volume=Decimal(15),
            remark='Remarque 1',
            course_summary='Course summary',
        )
        self.serializer = ApplicationSerializer()

    def test_assert_serialize_to_delete_epc_message(self):
        obj_serialized = self.serializer.serialize_to_delete_epc_message(self.application)

        self.assertEqual(obj_serialized['operation'], 'delete')
        self.assertEqual(obj_serialized['remark'], self.application.remark)
        self.assertEqual(obj_serialized['global_id'], self.application.applicant_id.global_id)
        self.assertEqual(obj_serialized['course_summary'], self.application.course_summary)
        self.assertEqual(obj_serialized['lecturing_allocation'], str(self.application.lecturing_volume))
        self.assertEqual(obj_serialized['practical_allocation'], str(self.application.practical_volume))

        self.assertEqual(obj_serialized['learning_container_year']['reference'], '428750')
        self.assertEqual(
            obj_serialized['learning_container_year']['year'], self.application.vacant_course_id.year
        )
        self.assertEqual(
            obj_serialized['learning_container_year']['acronym'], str(self.application.vacant_course_id.code)
        )

    def test_assert_serialize_to_update_epc_message(self):
        obj_serialized = self.serializer.serialize_to_update_epc_message(self.application)

        self.assertEqual(obj_serialized['operation'], 'update')
        self.assertEqual(obj_serialized['remark'], self.application.remark)
        self.assertEqual(obj_serialized['course_summary'], self.application.course_summary)
        self.assertEqual(obj_serialized['global_id'], self.application.applicant_id.global_id)
        self.assertEqual(obj_serialized['lecturing_allocation'], str(self.application.lecturing_volume))
        self.assertEqual(obj_serialized['practical_allocation'], str(self.application.practical_volume))

        self.assertEqual(obj_serialized['learning_container_year']['reference'], '428750')
        self.assertEqual(
            obj_serialized['learning_container_year']['year'], self.application.vacant_course_id.year
        )
        self.assertEqual(
            obj_serialized['learning_container_year']['acronym'], str(self.application.vacant_course_id.code)
        )
