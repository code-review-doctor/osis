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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import operator

import factory.fuzzy

from base.tests.factories.entity import EntityFactory
from education_group.models.cohort_year import CohortYear
from education_group.models.enums.cohort_name import CohortName


class CohortYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CohortYear
        django_get_or_create = ('education_group_year', 'name',)

    education_group_year = factory.SubFactory("base.tests.factories.education_group_year.EducationGroupYearFactory")
    administration_entity = factory.SubFactory(EntityFactory)
    name = factory.Iterator(CohortName.choices(), getter=operator.itemgetter(0))

    class Params:
        first_year_bachelor = factory.Trait(
            name=CohortName.FIRST_YEAR.name
        )
