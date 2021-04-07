import mock
from django.test import TestCase

from attribution.auth import predicates
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.auth.roles.tutor import Tutor
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory


class TestUserHaveAttributionOnLearningUnitYear(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year = LearningUnitYearFactory()

    def setUp(self):
        self.person = PersonFactory()
        self.predicate_context_mock = mock.patch(
            "rules.Predicate.context",
            new_callable=mock.PropertyMock,
            return_value={
                'role_qs': Tutor.objects.filter(person=self.person),
                'perm_name': 'dummy-perm'
            }
        )
        self.predicate_context_mock.start()
        self.addCleanup(self.predicate_context_mock.stop)

    def test_have_attribution_on_learning_unit(self):
        AttributionChargeNewFactory(
            attribution__tutor__person=self.person,
            learning_component_year__learning_unit_year=self.learning_unit_year
        )

        self.assertTrue(
            predicates.have_attribution_on_learning_unit_year(self.person.user, self.learning_unit_year)
        )

    def test_not_have_attribution_on_learning_unit(self):
        self.assertFalse(
            predicates.have_attribution_on_learning_unit_year(self.person.user, self.learning_unit_year)
        )
