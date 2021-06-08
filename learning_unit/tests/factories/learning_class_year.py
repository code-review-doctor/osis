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
import operator
import string

import factory.fuzzy

from base.models.enums import learning_unit_year_session, quadrimesters
from base.tests.factories.campus import CampusFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from continuing_education.tests.utils.utils import get_enum_keys


class LearningClassYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "learning_unit.LearningClassYear"

    learning_component_year = factory.SubFactory(LearningComponentYearFactory)
    acronym = factory.fuzzy.FuzzyText(length=1,
                                      chars=string.ascii_uppercase + string.digits)

    hourly_volume_partial_q1 = factory.fuzzy.FuzzyDecimal(0, 30, precision=0)
    hourly_volume_partial_q2 = factory.fuzzy.FuzzyDecimal(0, 30, precision=0)
    session = factory.Iterator(learning_unit_year_session.LEARNING_UNIT_YEAR_SESSION, getter=operator.itemgetter(0))
    quadrimester = factory.Iterator(quadrimesters.LearningUnitYearQuadrimester.choices(),
                                    getter=operator.itemgetter(0))
    campus = factory.SubFactory(CampusFactory)
    title_fr = factory.Sequence(lambda n: 'Learning class year - %d' % n)
    title_en = factory.Sequence(lambda n: 'Learning class year english - %d' % n)
