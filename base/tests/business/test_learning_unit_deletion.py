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
from unittest import mock

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from assistant.models.tutoring_learning_unit_year import TutoringLearningUnitYear
from assistant.tests.factories.assistant_mandate import AssistantMandateFactory
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from attribution.tests.factories.attribution_new import AttributionNewFactory
from attribution.tests.factories.tutor_application import TutorApplicationFactory
from base.business.learning_unit import CMS_LABEL_SPECIFICATIONS, CMS_LABEL_PEDAGOGY, CMS_LABEL_SUMMARY
from base.business.learning_units.simple import deletion
from base.models.enums import entity_type
from base.models.enums import learning_container_year_types
from base.models.enums import learning_unit_year_subtypes
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_calendar import generate_learning_unit_edition_calendars
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import CatalogViewerFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from cms.models.translated_text import TranslatedText
from cms.tests.factories.text_label import LearningUnitYearTextLabelFactory
from cms.tests.factories.translated_text import LearningUnitYearTranslatedTextFactory
from learning_unit.models.learning_class_year import LearningClassYear
from learning_unit.tests.factories.central_manager import CentralManagerFactory
from learning_unit.tests.factories.faculty_manager import FacultyManagerFactory
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory
from program_management.tests.factories.element import ElementFactory


class LearningUnitYearDeletion(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()
        cls.learning_unit = LearningUnitFactory(start_year__year=1900)
        cls.l_container_year = LearningContainerYearFactory()
        cls.luy1 = LearningUnitYearFactory(
            acronym="LBIR1212",
            learning_container_year=cls.l_container_year,
            academic_year=cls.academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=cls.learning_unit)
        cls.the_partim = _('The partim')
        generate_learning_unit_edition_calendars([cls.academic_year])

    def test_check_related_partims_deletion(self):
        msg = deletion._check_related_partims_deletion(self.l_container_year)
        self.assertEqual(len(msg.values()), 0)

        l_unit_2 = LearningUnitYearFactory(acronym="LBIR1213", learning_container_year=self.l_container_year,
                                           academic_year=self.academic_year, subtype=learning_unit_year_subtypes.PARTIM)

        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)
        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)
        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)

        elem_ue_1 = ElementFactory(learning_unit_year=l_unit_2)
        elem_ue_2 = ElementFactory(learning_unit_year=l_unit_2)

        group_1 = GroupElementYearFactory(child_element=elem_ue_1)
        group_2 = GroupElementYearFactory(child_element=elem_ue_2)

        component = LearningComponentYearFactory(learning_unit_year=l_unit_2)

        attribution_1 = AttributionNewFactory(learning_container_year=l_unit_2.learning_container_year)
        attribution_2 = AttributionNewFactory(learning_container_year=l_unit_2.learning_container_year)

        AttributionChargeNewFactory(learning_component_year=component,
                                    attribution=attribution_1)
        AttributionChargeNewFactory(learning_component_year=component,
                                    attribution=attribution_1)
        AttributionChargeNewFactory(learning_component_year=component,
                                    attribution=attribution_2)

        msg = deletion._check_related_partims_deletion(self.l_container_year)
        msg = list(msg.values())

        self.assertEqual(len(msg), 5)
        self.assertIn(
            _("There is %(count)d enrollments in %(subtype)s %(acronym)s for the year %(year)s") % {
                'subtype': self.the_partim,
                'acronym': l_unit_2.acronym,
                'year': l_unit_2.academic_year,
                'count': 3
            },
            msg
        )

        msg_delete_tutor = _("%(subtype)s %(acronym)s is assigned to %(tutor)s for the year %(year)s")
        self.assertIn(msg_delete_tutor % {'subtype': self.the_partim,
                                          'acronym': l_unit_2.acronym,
                                          'year': l_unit_2.academic_year,
                                          'tutor': attribution_1.tutor},
                      msg)
        self.assertIn(msg_delete_tutor % {'subtype': self.the_partim,
                                          'acronym': l_unit_2.acronym,
                                          'year': l_unit_2.academic_year,
                                          'tutor': attribution_2.tutor},
                      msg)

        msg_delete_offer_type = _('%(subtype)s %(acronym)s is included in the group %(group)s for the year %(year)s')

        self.assertIn(msg_delete_offer_type
                      % {'subtype': self.the_partim,
                         'acronym': l_unit_2.acronym,
                         'group': group_1.parent_element.group_year.partial_acronym,
                         'year': l_unit_2.academic_year},
                      msg)
        self.assertIn(msg_delete_offer_type
                      % {'subtype': self.the_partim,
                         'acronym': l_unit_2.acronym,
                         'group': group_2.parent_element.group_year.partial_acronym,
                         'year': l_unit_2.academic_year},
                      msg)

    def test_check_learning_unit_year_deletion(self):
        msg = deletion.check_learning_unit_year_deletion(self.luy1)

        msg = list(msg.values())
        self.assertEqual(msg, [])

        l_unit_2 = LearningUnitYearFactory(acronym="LBIR1212A", learning_container_year=self.l_container_year,
                                           academic_year=self.academic_year, subtype=learning_unit_year_subtypes.PARTIM)
        LearningUnitYearFactory(acronym="LBIR1212B", learning_container_year=self.l_container_year,
                                academic_year=self.academic_year, subtype=learning_unit_year_subtypes.PARTIM)

        LearningUnitEnrollmentFactory(learning_unit_year=self.luy1)
        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)

        msg = deletion.check_learning_unit_year_deletion(self.luy1)

        msg = list(msg.values())
        self.assertEqual(len(msg), 2)

    def test_check_learning_unit_year_deletion_with_proposal(self):
        ProposalLearningUnitFactory(learning_unit_year=self.luy1)
        msg = deletion._check_learning_unit_proposal(self.luy1)

        msg = list(msg.values())
        self.assertEqual(msg, [
            _("%(subtype)s %(acronym)s is in proposal for the year %(year)s") % {'subtype': _('The learning unit'),
                                                                                 'acronym': self.luy1.acronym,
                                                                                 'year': self.luy1.academic_year}
        ])

    def test_delete_next_years(self):
        l_unit = LearningUnitFactory(start_year__year=1900)

        dict_learning_units = {}
        for year in range(2000, 2017):
            academic_year = AcademicYearFactory(year=year)
            dict_learning_units[year] = LearningUnitYearFactory(academic_year=academic_year, learning_unit=l_unit)

        year_to_delete = 2007
        msg = deletion.delete_from_given_learning_unit_year(dict_learning_units[year_to_delete])
        self.assertEqual(LearningUnitYear.objects.filter(academic_year__year__gte=year_to_delete,
                                                         learning_unit=l_unit).count(),
                         0)
        self.assertEqual(len(msg), 2017 - year_to_delete)
        self.assertEqual(l_unit.end_year.year, year_to_delete - 1)

    def test_delete_partim_from_full(self):
        l_container_year = LearningContainerYearFactory(academic_year=self.academic_year)
        l_unit_year = LearningUnitYearFactory(subtype=learning_unit_year_subtypes.FULL,
                                              learning_container_year=l_container_year,
                                              learning_unit=LearningUnitFactory(start_year__year=1900),
                                              academic_year=l_container_year.academic_year)

        l_unit_partim_1 = LearningUnitYearFactory(subtype=learning_unit_year_subtypes.PARTIM,
                                                  learning_container_year=l_container_year,
                                                  learning_unit=LearningUnitFactory(start_year__year=1900),
                                                  academic_year=l_container_year.academic_year)
        l_unit_partim_2 = LearningUnitYearFactory(subtype=learning_unit_year_subtypes.PARTIM,
                                                  learning_container_year=l_container_year,
                                                  learning_unit=LearningUnitFactory(start_year__year=1900),
                                                  academic_year=l_container_year.academic_year)

        deletion.delete_from_given_learning_unit_year(l_unit_year)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=l_unit_partim_1.id)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=l_unit_partim_2.id)

    def test_delete_learning_component_class(self):
        # Composant annualisé est associé à son composant et à son conteneur annualisé
        learning_component_year = LearningComponentYearFactory(
            acronym="/C",
            comment="TEST",
            learning_unit_year__learning_unit__start_year__year=1900
        )
        learning_container_year = learning_component_year.learning_unit_year.learning_container_year

        number_classes = 10
        for __ in range(number_classes):
            LearningClassYearFactory(learning_component_year=learning_component_year)

        learning_unit_year = learning_component_year.learning_unit_year
        learning_unit_year.subtype = learning_unit_year_subtypes.PARTIM
        learning_unit_year.save()

        msg = deletion.delete_from_given_learning_unit_year(learning_unit_year)

        msg_success = _("Learning unit %(acronym)s (%(academic_year)s) successfuly deleted.") % {
            'acronym': learning_unit_year.acronym,
            'academic_year': learning_unit_year.academic_year,
        }
        self.assertEqual(msg_success, msg.pop())

        self.assertEqual(LearningClassYear.objects.all().count(), 0)

        self.assertEqual(len(msg), number_classes)
        with self.assertRaises(ObjectDoesNotExist):
            LearningComponentYear.objects.get(id=learning_component_year.id)

        for classe in learning_component_year.learningclassyear_set.all():
            with self.assertRaises(ObjectDoesNotExist):
                LearningClassYear.objects.get(id=classe.id)

        # The learning_unit_container won't be deleted because the learning_unit_year is a partim
        self.assertEqual(learning_container_year, LearningContainerYear.objects.get(id=learning_container_year.id))

    def test_delete_learning_container_year(self):
        learning_container_year = LearningContainerYearFactory()

        learning_unit_year_full = LearningUnitYearFactory(learning_container_year=learning_container_year,
                                                          subtype=learning_unit_year_subtypes.FULL,
                                                          learning_unit=LearningUnitFactory(start_year__year=1900),
                                                          academic_year=learning_container_year.academic_year)
        learning_unit_year_partim = LearningUnitYearFactory(learning_container_year=learning_container_year,
                                                            subtype=learning_unit_year_subtypes.PARTIM,
                                                            learning_unit=LearningUnitFactory(start_year__year=1900),
                                                            academic_year=learning_container_year.academic_year)
        learning_unit_year_to_delete = LearningUnitYearFactory(learning_container_year=learning_container_year,
                                                               subtype=learning_unit_year_subtypes.PARTIM,
                                                               learning_unit=LearningUnitFactory(start_year__year=1900),
                                                               academic_year=learning_container_year.academic_year)

        deletion.delete_from_given_learning_unit_year(learning_unit_year_to_delete)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=learning_unit_year_to_delete.id)
        self.assertEqual(learning_unit_year_full, LearningUnitYear.objects.get(id=learning_unit_year_full.id))
        self.assertEqual(learning_container_year, LearningContainerYear.objects.get(id=learning_container_year.id))
        self.assertEqual(learning_unit_year_partim, LearningUnitYear.objects.get(id=learning_unit_year_partim.id))

        deletion.delete_from_given_learning_unit_year(learning_unit_year_partim)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=learning_unit_year_partim.id)
        self.assertEqual(learning_unit_year_full, LearningUnitYear.objects.get(id=learning_unit_year_full.id))
        self.assertEqual(learning_container_year, LearningContainerYear.objects.get(id=learning_container_year.id))

        deletion.delete_from_given_learning_unit_year(learning_unit_year_full)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=learning_unit_year_full.id)

        with self.assertRaises(ObjectDoesNotExist):
            LearningContainerYear.objects.get(id=learning_container_year.id)

    def test_delete_cms_data(self):
        """In this test, we will ensure that CMS data linked to the learning unit year is correctly deleted"""
        learning_container_year = LearningContainerYearFactory(academic_year=self.academic_year)
        learning_unit_year_to_delete = LearningUnitYearFactory(learning_container_year=learning_container_year,
                                                               subtype=learning_unit_year_subtypes.FULL,
                                                               academic_year=learning_container_year.academic_year)
        # Create CMS data - TAB Specification
        cms_specification_label = LearningUnitYearTextLabelFactory(label=CMS_LABEL_SPECIFICATIONS[0])
        LearningUnitYearTranslatedTextFactory(reference=learning_unit_year_to_delete.pk,
                                              text_label=cms_specification_label,
                                              text='Specification of learning unit year')
        # Create CMS data - TAB Pedagogy
        cms_pedagogy_label = LearningUnitYearTextLabelFactory(label=CMS_LABEL_PEDAGOGY[0])
        LearningUnitYearTranslatedTextFactory(reference=learning_unit_year_to_delete.pk,
                                              text_label=cms_pedagogy_label, text='Pedagogy of learning unit year')
        # Create CMS data - TAB Summary
        cms_summary_label = LearningUnitYearTextLabelFactory(label=CMS_LABEL_SUMMARY[0])
        LearningUnitYearTranslatedTextFactory(reference=learning_unit_year_to_delete.pk,
                                              text_label=cms_summary_label, text='Summary of learning unit year')

        # Before delete, we should have 3 data in CMS
        self.assertEqual(3, TranslatedText.objects.all().count())

        deletion._delete_cms_data(learning_unit_year_to_delete)

        # After deletion, we should have no data in CMS
        self.assertFalse(TranslatedText.objects.all().count())

    def test_check_delete_learning_unit_year_with_assistants(self):
        learning_unit_year = LearningUnitYearFactory()
        assistant_mandate = AssistantMandateFactory()
        tutoring = TutoringLearningUnitYear.objects.create(mandate=assistant_mandate,
                                                           learning_unit_year=learning_unit_year)

        msg = deletion.check_learning_unit_year_deletion(learning_unit_year)
        self.assertIn(tutoring, msg.keys())

    def test_can_delete_learning_unit_year_with_faculty_manager_role(self):
        # Faculty manager can only delete other type than COURSE/INTERNSHIP/DISSERTATION
        entity_version = EntityVersionFactory(
            entity_type=entity_type.FACULTY,
            acronym="SST",
            start_date=datetime.date(year=1990, month=1, day=1),
            end_date=None
        )
        manager = FacultyManagerFactory(entity=entity_version.entity)

        # Creation UE
        l_containeryear = LearningContainerYearFactory(
            academic_year=self.academic_year,
            container_type=learning_container_year_types.COURSE,
            requirement_entity=entity_version.entity
        )
        learning_unit_year = LearningUnitYearFactory(
            academic_year=self.academic_year,
            learning_container_year=l_containeryear,
            subtype=learning_unit_year_subtypes.FULL
        )

        # Cannot remove FULL COURSE
        self.assertFalse(manager.person.user.has_perm('base.can_delete_learningunit', learning_unit_year))

        # Can remove PARTIM COURSE
        learning_unit_year = LearningUnitYearFactory(
            academic_year=self.academic_year,
            learning_container_year=l_containeryear,
            subtype=learning_unit_year_subtypes.PARTIM
        )
        self.assertTrue(manager.person.user.has_perm('base.can_delete_learningunit', learning_unit_year))

        # invalidate cache
        del manager.person.user._group_cache

        # With both role, greatest is taken
        CentralManagerFactory(person=manager.person, entity=entity_version.entity)
        learning_unit_year.subtype = learning_unit_year_subtypes.FULL
        learning_unit_year.save()

        self.assertTrue(manager.person.user.has_perm('base.can_delete_learningunit', learning_unit_year))

    def test_cannot_delete_learning_unit_year_with_catalog_viewer_role(self):
        catalog_viewer = CatalogViewerFactory()
        EntityVersionFactory(entity_type=entity_type.FACULTY, acronym="SST",
                             start_date=datetime.date(year=1990, month=1, day=1),
                             end_date=None)
        # Cannot remove FULL COURSE
        self.assertFalse(catalog_viewer.user.has_perm('base.can_delete_learningunit', self.luy1))

        # Cannot remove PARTIM COURSE
        self.luy1.subtype = learning_unit_year_subtypes.PARTIM
        self.luy1.save()
        self.assertFalse(catalog_viewer.user.has_perm('base.can_delete_learningunit', self.luy1))
        self.luy1.subtype = learning_unit_year_subtypes.FULL
        self.luy1.save()

    @mock.patch("base.models.person.Person.is_linked_to_entity_in_charge_of_learning_unit_year", return_value=True)
    def test_cannot_delete_if_has_application_same_year(self, mock_is_linked):
        luy = LearningUnitYearFactory(subtype=learning_unit_year_subtypes.FULL)
        manager = CentralManagerFactory(entity=luy.requirement_entity)
        TutorApplicationFactory(learning_container_year=luy.learning_container_year)
        self.assertFalse(manager.person.user.has_perm('base.can_delete_learningunit', luy))

    @mock.patch("base.models.person.Person.is_linked_to_entity_in_charge_of_learning_unit_year", return_value=True)
    def test_cannot_delete_partim_if_has_application(self, mock_is_linked):
        luy = LearningUnitYearFactory(subtype=learning_unit_year_subtypes.PARTIM)
        manager = CentralManagerFactory(entity=luy.requirement_entity)
        AttributionChargeNewFactory(learning_component_year__learning_unit_year=luy)
        self.assertFalse(manager.person.user.has_perm('base.can_delete_learningunit', luy))

    @mock.patch("base.models.person.Person.is_linked_to_entity_in_charge_of_learning_unit_year", return_value=True)
    def test_cannot_delete_if_has_application_another_year(self, mock_is_linked):
        next_anac = AcademicYearFactory(year=self.academic_year.year + 1)
        luy_next_year = LearningUnitYearFactory(
            learning_unit=self.learning_unit,
            academic_year=next_anac,
            learning_container_year=LearningContainerYearFactory(
                academic_year=next_anac,
                learning_container=self.l_container_year.learning_container
            ),
            subtype=learning_unit_year_subtypes.FULL,
        )
        manager = CentralManagerFactory(entity=luy_next_year.requirement_entity)
        TutorApplicationFactory(learning_container_year=self.luy1.learning_container_year)
        self.assertFalse(manager.person.user.has_perm('base.can_delete_learningunit', luy_next_year))
