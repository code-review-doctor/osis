##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
import factory.fuzzy

from education_group.ddd.domain._diploma import Diploma, DiplomaAim, DiplomaAimIdentity


class DiplomaAimIdentityFactory(factory.Factory):
    class Meta:
        model = DiplomaAimIdentity
        abstract = False

    section = factory.Sequence(lambda n: 'Aim section %02d' % n)
    code = factory.Sequence(lambda n: '%02d' % n)


class DiplomaAimFactory(factory.Factory):
    class Meta:
        model = DiplomaAim
        abstract = False

    entity_id = factory.SubFactory(DiplomaAimIdentityFactory)
    description = factory.fuzzy.FuzzyText()


class DiplomaFactory(factory.Factory):
    class Meta:
        model = Diploma
        abstract = False

    leads_to_diploma = True
    printing_title = factory.Sequence(lambda n: 'Printing title %02d' % n)
    professional_title = factory.Sequence(lambda n: 'Professionnal title %02d' % n)
    aims = []

    class Params:
        with_aims = factory.Trait(aims=[DiplomaAimFactory(), DiplomaAimFactory()])
