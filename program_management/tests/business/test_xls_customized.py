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
from django.test import TestCase, SimpleTestCase


from program_management.business.xls_customized import _build_headers, TRAINING_LIST_CUSTOMIZABLE_PARAMETERS, \
    WITH_ACTIVITIES, WITH_ORGANIZATION, WITH_OTHER_LEGAL_INFORMATION, WITH_ARES_CODE, WITH_CO_GRADUATION_AND_PARTNERSHIP
from django.test.utils import override_settings

DEFAULT_FR_HEADERS = ['Anac.', 'Sigle/Int. abr.', 'Intitulé', 'Catégorie', 'Type', 'Crédits']
VALIDITY_HEADERS = ["Statut", "Début", "Dernière année d'org."]
PARTIAL_ENGLISH_TITLES = ["Intitulé en anglais", "Intitulé partiel en français", "Intitulé partiel en anglais", ]
EDUCATION_FIELDS_HEADERS = ["Domaine principal", "Domaines secondaires", "Domaine ISCED/CITE"]
ACTIVITIES_HEADERS = [
    "Activités sur d'autres sites", "Stage", "Mémoire", "Langue principale", "Activités en anglais",
    "Activités dans d'autres langues"
]
ORGANIZATION_HEADERS = [
    "Type horaire", "Ent. gestion", "Ent. adm.", "Lieu d'enseignement", "Durée"
] + ACTIVITIES_HEADERS


ARES_HEADERS_ONLY = ["Code étude ARES", "ARES-GRACA", "Habilitation ARES"]

CO_GRADUATION_AND_PARTNERSHIP_COMMON_WITH_ARES_HEADERS = [
    "Code co-diplômation intra CfB", "Coefficient total de co-diplômation"
]

CO_GRADUATION_AND_PARTNERSHIP_HEADERS = CO_GRADUATION_AND_PARTNERSHIP_COMMON_WITH_ARES_HEADERS +\
                                        ["Programme co-organisés avec d'autres institutions"]


ARES_HEADERS = CO_GRADUATION_AND_PARTNERSHIP_COMMON_WITH_ARES_HEADERS + ARES_HEADERS_ONLY

DIPLOMA_CERTIFICAT_HEADERS = [
    "Mène à diplôme/certificat", "Intitulé du diplôme/du certificat", "Titre professionnel", "Attendus du diplôme"
    ]
ENROLLMENT_HEADERS = [
    "Lieu d'inscription", "Inscriptible", "Ré-inscription par internet", "Sous-épreuve", "Concours", "Code tarif"
]

FUNDING_HEADERS = [
    "Finançable", "Orientation de financement", "Financement coopération internationale CCD/CUD",
    "Orientation coopération internationale CCD/CUD"
]
OTHER_LEGAL_INFORMATION_HEADERS = ["Nature", "Certificat universitaire", "Catégorie décret"]
ADDITIONAL_INFO_HEADERS = [
    "Type de contrainte", "Contrainte minimum", "Contrainte maximum", "Commentaire (interne)", "Remarque",
    "Remarque en anglais"
]


@override_settings(LANGUAGES=[('fr-be', 'Français'), ], LANGUAGE_CODE='fr-be')
class XlsCustomizedTestCase(SimpleTestCase):

    def test_headers_without_selected_parameters(self):
        expected = DEFAULT_FR_HEADERS
        self.assertListEqual(_build_headers([]), expected)

    def test_headers_with_all_parameters_selected(self):
        headers = _build_headers(TRAINING_LIST_CUSTOMIZABLE_PARAMETERS)
        self.assertListEqual(headers[0:6], DEFAULT_FR_HEADERS)
        self.assertListEqual(headers[6:9], VALIDITY_HEADERS)
        self.assertListEqual(headers[9:10], ["Code"])
        self.assertListEqual(headers[10:13], PARTIAL_ENGLISH_TITLES)
        self.assertListEqual(headers[13:16], EDUCATION_FIELDS_HEADERS)
        self.assertListEqual(headers[16:27], ORGANIZATION_HEADERS)
        self.assertListEqual(headers[27:28], ["Infos générales - contacts"])
        self.assertListEqual(headers[28:32], DIPLOMA_CERTIFICAT_HEADERS)
        self.assertListEqual(headers[32:35], CO_GRADUATION_AND_PARTNERSHIP_HEADERS)
        self.assertListEqual(headers[35:41], ENROLLMENT_HEADERS)
        self.assertListEqual(headers[41:45], FUNDING_HEADERS)
        self.assertListEqual(headers[45:48], ARES_HEADERS_ONLY)
        self.assertListEqual(headers[48:51], OTHER_LEGAL_INFORMATION_HEADERS)
        self.assertListEqual(headers[51:57], ADDITIONAL_INFO_HEADERS)
        self.assertListEqual(headers[57:58], ["Mots clés"])


    def test_no_duplicate_headers_when_organization_and_activities(self):
        headers = _build_headers([WITH_ORGANIZATION, WITH_ACTIVITIES])
        self.assertListEqual(headers[0:6], DEFAULT_FR_HEADERS)
        self.assertListEqual(headers[6:], ORGANIZATION_HEADERS)

    def test_no_duplicate_headers_when_organization_and_without_activities(self):
        headers = _build_headers([WITH_ORGANIZATION])
        self.assertListEqual(headers[0:6], DEFAULT_FR_HEADERS)
        self.assertListEqual(headers[6:], ORGANIZATION_HEADERS)

    def test_no_duplicate_headers_without_organization_and_with_activities(self):
        headers = _build_headers([WITH_ACTIVITIES])
        self.assertListEqual(headers[0:6], DEFAULT_FR_HEADERS)
        self.assertListEqual(headers[6:], ACTIVITIES_HEADERS)

    def test_no_duplicate_headers_with_co_graduation_and_partnership_and_ares_code(self):
        headers = _build_headers([WITH_CO_GRADUATION_AND_PARTNERSHIP, WITH_ARES_CODE])
        self.assertListEqual(headers[0:6], DEFAULT_FR_HEADERS)
        self.assertListEqual(headers[6:], CO_GRADUATION_AND_PARTNERSHIP_HEADERS + ARES_HEADERS_ONLY)

    def test_headers_without_co_graduation_and_partnership_and_with_ares_code(self):
        headers = _build_headers([WITH_ARES_CODE])
        self.assertListEqual(headers[0:6], DEFAULT_FR_HEADERS)
        self.assertListEqual(headers[6:], ARES_HEADERS)

    def test_headers_with_co_graduation_and_partnership_and_without_ares_code(self):
        headers = _build_headers([WITH_CO_GRADUATION_AND_PARTNERSHIP])
        self.assertListEqual(headers[0:6], DEFAULT_FR_HEADERS)
        self.assertListEqual(headers[6:], CO_GRADUATION_AND_PARTNERSHIP_HEADERS)
