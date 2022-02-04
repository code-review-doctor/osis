##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import factory
from factory import fuzzy

from base.tests.factories.organization import OrganizationFactory
from reference.tests.factories.city import ZipCodeFactory
from reference.tests.factories.language import LanguageFactory


class HighSchoolFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'reference.HighSchool'

    external_id = factory.Faker('text', max_nb_chars=100)
    # uuid
    organization = factory.SubFactory(OrganizationFactory)
    phone = factory.Sequence(lambda n: 'Phone - %d' % n)
    fax = factory.Sequence(lambda n: 'Fax - %d' % n)
    email = factory.Sequence(lambda n: 'high_school{0}@example.com'.format(n))
    start_year = fuzzy.FuzzyInteger(1999, 2099)
    end_year = None
    linguistic_regime = factory.SubFactory(LanguageFactory)
    zip_code = factory.SubFactory(ZipCodeFactory)
    street = factory.Sequence(lambda n: 'Street {0}'.format(n))
    street_number = factory.Sequence(lambda n: '%d' % n)
    type = ''
