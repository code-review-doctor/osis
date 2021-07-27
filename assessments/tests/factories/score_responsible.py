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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

import factory.fuzzy

from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.tutor import TutorFactory
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory


class ScoreResponsibleFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'assessments.ScoreResponsible'

    tutor = factory.SubFactory(TutorFactory)
    learning_unit_year = factory.SubFactory(LearningUnitYearFactory)
    learning_class_year = None


class ScoreResponsibleOfClassFactory(ScoreResponsibleFactory):
    learning_class_year = factory.SubFactory(
        LearningClassYearFactory,
        learning_component_year__learning_unit_year=factory.LazyAttribute(
            lambda component: component.factory_parent.factory_parent.learning_unit_year
        )
    )
