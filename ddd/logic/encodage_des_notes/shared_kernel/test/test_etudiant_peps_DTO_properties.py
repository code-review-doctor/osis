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

from django.test import SimpleTestCase
from django.utils.translation import ugettext as _

from base.models.enums.peps_type import PepsTypes, HtmSubtypes, SportSubtypes
from ddd.logic.encodage_des_notes.shared_kernel.dtos import EtudiantPepsDTO


class EtudiantPepsDtoPropertiesTest(SimpleTestCase):

    def test_assert_type_peps_disability_correctly_formatted(self):
        peps = EtudiantPepsDTO(
            type_peps=PepsTypes.DISABILITY.name,
            sous_type_peps=HtmSubtypes.REDUCED_MOBILITY.name,
            tiers_temps=False,
            copie_adaptee=False,
            local_specifique=False,
            autre_amenagement=False,
            details_autre_amenagement='',
            accompagnateur='',
        )
        expected_result = "{} - {}".format(str(PepsTypes.DISABILITY.value), str(HtmSubtypes.REDUCED_MOBILITY.value))
        self.assertEqual(peps.get_type_peps_display, expected_result)

    def test_assert_type_peps_sport_correctly_formatted(self):
        peps = EtudiantPepsDTO(
            type_peps=PepsTypes.SPORT.name,
            sous_type_peps=SportSubtypes.PROMISING_ATHLETE.name,
            tiers_temps=False,
            copie_adaptee=False,
            local_specifique=False,
            autre_amenagement=False,
            details_autre_amenagement='',
            accompagnateur='',
        )
        expected_result = "{} - {}".format(str(PepsTypes.SPORT.value), str(SportSubtypes.PROMISING_ATHLETE.value))
        self.assertEqual(peps.get_type_peps_display, expected_result)

    def test_assert_type_peps_not_defined_correctly_formatted(self):
        peps = EtudiantPepsDTO(
            type_peps=PepsTypes.NOT_DEFINED.name,
            sous_type_peps='',
            tiers_temps=False,
            copie_adaptee=False,
            local_specifique=False,
            autre_amenagement=False,
            details_autre_amenagement='',
            accompagnateur='',
        )
        self.assertEqual(peps.get_type_peps_display, "-")

    def test_assert_amenagement_correctly_formatted(self):
        peps = EtudiantPepsDTO(
            type_peps=PepsTypes.NOT_DEFINED.name,
            sous_type_peps='',
            tiers_temps=True,
            copie_adaptee=True,
            local_specifique=True,
            autre_amenagement=True,
            details_autre_amenagement='Allègement du PAE',
            accompagnateur='SANNA, Alice',
        )
        expected = [
                _('Extra time (33% generally)'),
                _('Large print'),
                _('Specific room of examination'),
                _('Other educational facilities'),
                '{} : Allègement du PAE'.format(_('Details other educational facilities'))
            ]
        self.assertListEqual(peps.get_arrangements_display, expected)
