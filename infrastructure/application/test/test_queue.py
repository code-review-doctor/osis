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
import copy
import json

from django.test import TestCase

from attribution.models.tutor_application import TutorApplication
from attribution.tests.factories.tutor_application import TutorApplicationFactory
from base.tests.factories.tutor import TutorFactory
from infrastructure.application import queue


class ApplicationUpdateResponseCallbackTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory(person__global_id='987654321')
        cls.tutor_application_ldroi1200 = TutorApplicationFactory(
            tutor=cls.tutor,
            learning_container_year__acronym='LDROI1200',
            learning_container_year__academic_year__year=2022,
            external_id=''
        )
        cls.tutor_application_lagro1500 = TutorApplicationFactory(
            tutor=cls.tutor,
            learning_container_year__acronym='LAGRO1500',
            learning_container_year__academic_year__year=2022,
            external_id='osis.tutor_application_23456697'
        )

    def setUp(self) -> None:
        self.epc_response_ldroi1200 = {
            'operation': 'update',
            'global_id': self.tutor.person.global_id,
            'learning_container_year': {
                'acronym': 'LDROI1200',
                'year': 2022
            },
            'num_ele_itv': '56478941'
        }

        self.epc_response_lagro1500 = {
            'operation': 'update',
            'global_id': self.tutor.person.global_id,
            'learning_container_year': {
                'acronym': 'LAGRO1500',
                'year': 2022
            },
            'num_ele_itv': '23456697'
        }

    def test_assert_right_external_id_computed_and_saved(self):
        epc_response = _encode_epc_response(self.epc_response_ldroi1200)
        queue.application_response_callback(epc_response)

        self.tutor_application_ldroi1200.refresh_from_db()
        self.tutor_application_lagro1500.refresh_from_db()

        expected_external_id = 'osis.tutor_application_{num_ele_itv}'.format(
            num_ele_itv=self.epc_response_ldroi1200['num_ele_itv']
        )
        self.assertEqual(self.tutor_application_ldroi1200.external_id, expected_external_id)
        self.assertEqual(self.tutor_application_lagro1500.external_id, 'osis.tutor_application_23456697')

    def test_assert_raise_exception_when_error_in_payload_of_epc_response(self):
        epc_response_dict = {**self.epc_response_ldroi1200, 'error': 'An error occured in EPC'}
        epc_response = _encode_epc_response(epc_response_dict)

        with self.assertRaises(Exception):
            queue.application_response_callback(epc_response)

    def test_assert_raise_exception_when_missing_mandatory_payload_data(self):
        mandatory_fields = ['global_id', 'num_ele_itv', 'learning_container_year']
        for field in mandatory_fields:
            with self.subTest(field=field):
                epc_response_dict = copy.deepcopy(self.epc_response_ldroi1200)
                del epc_response_dict[field]
                epc_response = _encode_epc_response(epc_response_dict)

                with self.assertRaises(Exception):
                    queue.application_response_callback(epc_response)

    def test_case_external_id_already_set_and_external_id_computed_is_same_assert_nothing(self):
        epc_response = _encode_epc_response(self.epc_response_lagro1500)
        queue.application_response_callback(epc_response)

        self.assertEqual(self.tutor_application_lagro1500.external_id, 'osis.tutor_application_23456697')

    def test_case_external_id_already_set_and_external_id_computed_is_different_assert_raise_exception(self):
        epc_response_dict = {**self.epc_response_lagro1500, 'num_ele_itv': '5632114798'}
        epc_response = _encode_epc_response(epc_response_dict)

        with self.assertRaises(Exception):
            queue.application_response_callback(epc_response)


class ApplicationDeleteResponseCallbackTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory(person__global_id='987654321')

    def setUp(self) -> None:
        self.tutor_application_lfopa1650 = TutorApplicationFactory(
            tutor=self.tutor,
            learning_container_year__acronym='LFOPA1650',
            learning_container_year__academic_year__year=2022,
            external_id='osis.tutor_application_23456697'
        )

        self.epc_response_lfopa1650 = {
            'operation': 'delete',
            'global_id': self.tutor.person.global_id,
            'learning_container_year': {
                'acronym': 'LFOPA1650',
                'year': 2022
            },
            'num_ele_itv': '23456697'
        }

    def test_assert_application_correctly_deleted(self):
        epc_response = _encode_epc_response(self.epc_response_lfopa1650)
        queue.application_response_callback(epc_response)

        self.assertFalse(TutorApplication.objects.filter(external_id='osis.tutor_application_23456697').exists())


def _encode_epc_response(epc_response: dict):
    epc_response_str = json.dumps(epc_response)
    return epc_response_str.encode()