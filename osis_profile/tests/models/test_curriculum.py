# ##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
# ##############################################################################

from django.test import TestCase

from base.tests.factories.person import PersonFactory
from osis_profile.models import CurriculumYear
from osis_profile.models.curriculum import curriculum_directory_path
from osis_profile.tests.factories.curriculum import ExperienceFactory, CurriculumYearFactory
from reference.tests.factories.country import CountryFactory


class CurriculumExperienceTestCase(TestCase):

    def test_on_delete_delete_previous_curriculum_year_if_empty(self):
        # Create a new curriculum year
        curriculum_year = CurriculumYearFactory()
        self.assertEqual(curriculum_year.experiences.count(), 0)
        # Links a new experience to this curriculum year
        experience = ExperienceFactory(curriculum_year=curriculum_year, country=CountryFactory())
        # The curriculum year contains this experience
        self.assertEqual(CurriculumYear.objects.get(pk=curriculum_year.pk).experiences.count(), 1)
        # Delete the experience
        experience.delete()
        # The curriculum year has been deleted
        self.assertFalse(CurriculumYear.objects.filter(pk=curriculum_year.pk).exists())

    def test_on_delete_keep_previous_curriculum_year_if_not_empty(self):
        # Create a new curriculum year
        curriculum_year = CurriculumYearFactory()
        self.assertEqual(curriculum_year.experiences.count(), 0)
        # Links a new experience to this curriculum year
        first_experience = ExperienceFactory(curriculum_year=curriculum_year, country=CountryFactory())
        # Create a second experience related to the same curriculum year
        second_experience = ExperienceFactory(curriculum_year=curriculum_year, country=CountryFactory())
        # The curriculum year contains the two experiences
        self.assertEqual(CurriculumYear.objects.get(pk=curriculum_year.pk).experiences.count(), 2)
        # Delete one experience
        second_experience.delete()
        # The curriculum year has not been deleted and still contains one experience
        first_curriculum_year = CurriculumYear.objects.filter(pk=curriculum_year.pk)
        self.assertEqual(first_curriculum_year.count(), 1)
        self.assertEqual(first_curriculum_year.first().experiences.count(), 1)
        self.assertEqual(first_curriculum_year.first().experiences.first().pk, first_experience.id)

    def test_on_update_delete_previous_curriculum_year_if_empty(self):
        # Create two new curriculum years
        first_curriculum_year = CurriculumYearFactory()
        second_curriculum_year = CurriculumYearFactory()
        self.assertEqual(first_curriculum_year.experiences.count(), 0)
        # Links a new experience to the first curriculum year
        experience = ExperienceFactory(curriculum_year=first_curriculum_year, country=CountryFactory())
        # The first curriculum year contains this experience
        self.assertEqual(CurriculumYear.objects.get(pk=first_curriculum_year.pk).experiences.count(), 1)
        # Update the experience
        experience.curriculum_year = second_curriculum_year
        experience.save()
        # The first curriculum year has been deleted
        self.assertFalse(CurriculumYear.objects.filter(pk=first_curriculum_year.pk).exists())
        # The second curriculum year contains now this experience
        second_curriculum_year = CurriculumYear.objects.filter(pk=second_curriculum_year.pk)
        self.assertEqual(second_curriculum_year.count(), 1)
        self.assertEqual(second_curriculum_year.first().experiences.count(), 1)
        self.assertEqual(second_curriculum_year.first().experiences.first().pk, experience.id)

    def test_on_update_keep_previous_curriculum_year_if_not_empty(self):
        # Create two new curriculum years
        first_curriculum_year = CurriculumYearFactory()
        second_curriculum_year = CurriculumYearFactory()
        # Links two experiences to the first curriculum year
        first_experience = ExperienceFactory(curriculum_year=first_curriculum_year, country=CountryFactory())
        second_experience = ExperienceFactory(curriculum_year=first_curriculum_year, country=CountryFactory())
        # The first curriculum year contains these experiences
        self.assertEqual(CurriculumYear.objects.get(pk=first_curriculum_year.pk).experiences.count(), 2)
        # Update the experience
        first_experience.curriculum_year = second_curriculum_year
        first_experience.save()
        # The second curriculum year contains now this experience
        second_curriculum_year = CurriculumYear.objects.filter(pk=second_curriculum_year.pk)
        self.assertEqual(second_curriculum_year.count(), 1)
        self.assertEqual(second_curriculum_year.first().experiences.count(), 1)
        self.assertEqual(second_curriculum_year.first().experiences.first().pk, first_experience.id)
        # The first curriculum year has not been deleted and still contains the other experience
        first_curriculum_year = CurriculumYear.objects.filter(pk=first_curriculum_year.pk)
        self.assertEqual(first_curriculum_year.count(), 1)
        self.assertEqual(first_curriculum_year.first().experiences.count(), 1)
        self.assertEqual(first_curriculum_year.first().experiences.first().pk, second_experience.id)

    def test_upload_path(self):
        person = PersonFactory()
        curriculum_year = CurriculumYearFactory(person=person)
        experience = ExperienceFactory(curriculum_year=curriculum_year, country=CountryFactory())

        self.assertEqual(
            curriculum_directory_path(experience, 'file_name.pdf'),
            '{}/curriculum/file_name.pdf'.format(person.uuid)
        )
