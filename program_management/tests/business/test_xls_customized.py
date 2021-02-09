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
    WITH_ACTIVITIES, WITH_ORGANIZATION, WITH_ARES_CODE, WITH_CO_GRADUATION_AND_PARTNERSHIP, _build_additional_info
from django.test.utils import override_settings

from django.conf import settings
from django.db.models import F
from django.test import TestCase, RequestFactory
from django.urls import reverse

from base.models.enums import organization_type, education_group_types
from base.tests.factories.academic_year import AcademicYearFactory


from base.tests.factories.entity_version import EntityVersionFactory
from education_group.api.serializers.training import TrainingListSerializer, TrainingDetailSerializer
from program_management.models.education_group_version import EducationGroupVersion
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory, \
    StandardEducationGroupVersionFactory
from reference.tests.factories.domain import DomainFactory
from unittest import mock

from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.models.enums import academic_calendar_type
from base.tests.factories.academic_calendar import OpenAcademicCalendarFactory
from base.tests.factories.person import PersonFactory
from education_group.ddd.domain.exception import MiniTrainingNotFoundException, MiniTrainingHaveLinkWithEPC
from education_group.templatetags.academic_year_display import display_as_academic_year
from education_group.tests.factories.auth.central_manager import CentralManagerFactory
from education_group.tests.ddd.factories.training import TrainingFactory

from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.tests.ddd.factories.node import NodeGroupYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory
from program_management.tests.factories.education_group_version import StandardEducationGroupVersionFactory as \
    StandardEducationGroupVersionDbFactory
from education_group.ddd.domain.group import GroupIdentity
from program_management.tests.ddd.factories.node import NodeGroupYearFactory
from base.models.enums.education_group_categories import Categories
from base.models.enums.education_group_types import TrainingType, MiniTrainingType, GroupType
from base.tests.factories.academic_year import get_current_year
from base.tests.factories.person import PersonWithPermissionsFactory
from program_management.tests.factories.education_group_version import StandardEducationGroupVersionFactory
from program_management.tests.factories.element import ElementGroupYearFactory
from education_group.tests.ddd.factories.group import GroupFactory
from education_group.tests.ddd.factories.content_constraint import ContentConstraintFactory
from education_group.tests.ddd.factories.remark import RemarkFactory
from base.models.enums.constraint_type import ConstraintTypeEnum
from education_group.tests.factories.mini_training import MiniTrainingFactory
from education_group.ddd.domain.mini_training import MiniTrainingIdentity
from base.tests.factories.education_group_type import MiniTrainingEducationGroupTypeFactory

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
class XlsCustomizedHeadersTestCase(SimpleTestCase):

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


class XlsCustomizedContentForTrainingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_year = get_current_year()
        cls.person = PersonWithPermissionsFactory('view_educationgroup')
        cls.training_version = StandardEducationGroupVersionFactory(
            offer__acronym="DROI2M",
            offer__partial_acronym="LDROI200M",
            offer__academic_year__year=cls.current_year,
            offer__education_group_type__name=TrainingType.PGRM_MASTER_120.name,
            root_group__acronym="DROI2M",
            root_group__partial_acronym="LDROI200M",
            root_group__academic_year__year=cls.current_year,
            root_group__education_group_type__name=TrainingType.PGRM_MASTER_120.name,
        )
        cls.root_group_element = ElementGroupYearFactory(group_year=cls.training_version.root_group)
        # cls.group = cls.training_version.root_group
        cls.constraint = ContentConstraintFactory(type=ConstraintTypeEnum.CREDITS,
                                              minimum=1,
                                              maximum=15)

        cls.group_training = GroupFactory(entity_identity__code=cls.training_version.root_group.partial_acronym,
                                 entity_identity__year=cls.current_year,
                                 content_constraint=cls.constraint,
                                 remark=RemarkFactory(
                                     text_fr="<p>Remarque voir <a href='https://www.google.com/'>Google</a></p>",
                                     text_en="Remarque fr")
                                 )
        cls.training = TrainingFactory(entity_identity__acronym=cls.training_version.root_group.partial_acronym,
                                       entity_identity__year=cls.current_year,
                                       internal_comment='Internal comment')

    def test_build_additional_info_for_training(self):
        expected = [self.group_training.content_constraint.type.value.title(), self.group_training.content_constraint.minimum,
                    self.group_training.content_constraint.maximum, self.training.internal_comment,
                    "Remarque voir Google", self.group_training.remark.text_en]
        data = _build_additional_info(self.training, None, self.group_training)
        self.assertListEqual(data, expected)


class XlsCustomizedContentForMiniTrainingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_year = get_current_year()

        cls.mini_training_version = StandardEducationGroupVersionFactory(
            offer__acronym="DROI2M",
            offer__partial_acronym="LDROI200M",
            offer__academic_year__year=cls.current_year,
            offer__education_group_type__name=MiniTrainingType.DEEPENING.name,
            root_group__acronym="DROI2M",
            root_group__partial_acronym="LDROI200M",
            root_group__academic_year__year=cls.current_year,
            root_group__education_group_type__name=MiniTrainingType.DEEPENING.name,
        )
        cls.root_group_element = ElementGroupYearFactory(group_year=cls.mini_training_version.root_group)

        cls.constraint = ContentConstraintFactory(type=ConstraintTypeEnum.CREDITS,
                                                  minimum=1,
                                                  maximum=15)

        cls.group_training = GroupFactory(entity_identity__code=cls.mini_training_version.root_group.partial_acronym,
                                          entity_identity__year=cls.current_year,
                                          content_constraint=cls.constraint,
                                          remark=RemarkFactory(
                                              text_fr="<p>Remarque voir <a href='https://www.google.com/'>Google</a></p>",
                                              text_en="Remarque fr")
                                          )
        cls.education_group_type = MiniTrainingEducationGroupTypeFactory()
        cls.mini_training = MiniTrainingFactory(
            entity_identity=MiniTrainingIdentity(acronym="LOIS58", year=cls.current_year),
            start_year=cls.current_year,
            type=education_group_types.MiniTrainingType[cls.education_group_type.name],
        )
        cls.group_mini_training = GroupFactory(entity_identity__code=cls.mini_training_version.root_group.partial_acronym,
                                               entity_identity__year=cls.current_year,
                                               content_constraint=cls.constraint,
                                               remark=RemarkFactory(
                                                   text_fr="<p>Remarque voir <a href='https://www.google.com/'>Google</a></p>",
                                                   text_en="Remarque fr")
                                               )

    def test_build_additional_info_for_training(self):
        expected = [self.group_mini_training.content_constraint.type.value.title(),
                    self.group_mini_training.content_constraint.minimum,
                    self.group_mini_training.content_constraint.maximum, '',
                    "Remarque voir Google", self.group_mini_training.remark.text_en]
        data = _build_additional_info(None, self.mini_training, self.group_mini_training)
        self.assertListEqual(data, expected)


