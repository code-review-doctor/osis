##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.http import HttpResponse
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from assessments.api.views.score_sheets_pdf_export import ScoreSheetsPDFExportAPIView
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.tutor import TutorFactory
from ddd.logic.encodage_des_notes.shared_kernel.dtos import DateDTO, FeuilleDeNotesDTO, EnseignantDTO, DetailContactDTO, \
    NoteEtudiantDTO
from ddd.logic.encodage_des_notes.soumission.commands import SearchAdressesFeuilleDeNotesCommand, \
    GetFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.dtos import DonneesAdministrativesFeuilleDeNotesDTO, \
    AdresseFeuilleDeNotesDTO


class ScoreSheetsPDFExportAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.url = reverse('assessments_api_v1:' + ScoreSheetsPDFExportAPIView.name)

    def setUp(self):
        self.client.force_authenticate(user=self.tutor.person.user)

        self.patch_message_bus = mock.patch(
            "assessments.api.views.score_sheets_pdf_export.message_bus_instance.invoke",
            side_effect=self.__mock_message_bus_invoke
        )
        self.message_bus_mocked = self.patch_message_bus.start()
        self.addCleanup(self.patch_message_bus.stop)

    def __mock_message_bus_invoke(self, cmd):
        if isinstance(cmd, SearchAdressesFeuilleDeNotesCommand):
            return [
                DonneesAdministrativesFeuilleDeNotesDTO(
                    sigle_formation="DROI1BA",
                    code_unite_enseignement='LDROI1200',
                    date_deliberation=DateDTO.build_from_date(datetime.date.today()),
                    contact_feuille_de_notes=AdresseFeuilleDeNotesDTO(
                        nom_cohorte='DROI1BA',
                        entite='BUDR',
                        destinataire='',
                        rue_numero='',
                        code_postal='',
                        ville='',
                        pays='',
                        telephone='',
                        fax='',
                        email='',
                    ),
                )
            ]
        elif isinstance(cmd, GetFeuilleDeNotesCommand):
            return FeuilleDeNotesDTO(
                code_unite_enseignement='LDROI1200',
                intitule_complet_unite_enseignement='Introduction aux droits',
                responsable_note=EnseignantDTO(nom='Durant', prenom='Paul'),
                contact_responsable_notes=DetailContactDTO(
                    matricule_fgs="987654321",
                    email="paul.durant@email.be",
                    adresse_professionnelle=None,
                    langue="fr-be"
                ),
                autres_enseignants=[],
                annee_academique=2020,
                numero_session=2,
                note_decimale_est_autorisee=False,
                notes_etudiants=[
                    NoteEtudiantDTO(
                        code_unite_enseignement='LDROI1200',
                        annee_unite_enseignement=2021,
                        intitule_complet_unite_enseignement='Introduction au droit',
                        est_soumise=False,
                        date_remise_de_notes=DateDTO.build_from_date(
                            datetime.date.today() + datetime.timedelta(days=1)
                        ),
                        echeance_enseignant=DateDTO.build_from_date(
                            datetime.date.today() + datetime.timedelta(days=1)
                        ),
                        nom_cohorte='DROI1BA',
                        noma='999999999',
                        nom='Helios',
                        prenom='Jean',
                        peps=None,
                        email='dummy@gmail.com',
                        note=10,
                        inscrit_tardivement=False,
                        desinscrit_tardivement=False,
                    )
                ]
            )
        raise Exception('Bus Command not mocked in test')

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url, data={'codes': ['LDROI1200']})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_user_is_not_a_tutor_permission_denied(self):
        program_manager = ProgramManagerFactory()

        self.client.force_authenticate(user=program_manager.person.user)
        response = self.client.get(self.url, data={'codes': ['LDROI1200']})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch(
        'assessments.api.views.score_sheets_pdf_export.ScoreSheetsPDFExportAPIView.get',
        return_value=HttpResponse(content_type='application/pdf')
    )
    def test_get_assert_call_print_pdf(self, mock_print_notes):
        response = self.client.get(self.url, data={'codes': ['LDROI1200']})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_print_notes.called)
