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
import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class Titles(interface.ValueObject):
    common_fr = attr.ib(type=str)
    specific_fr = attr.ib(type=str)
    common_en = attr.ib(type=str)
    specific_en = attr.ib(type=str)

    @property
    def complete_fr(self) -> str:
        if self.common_fr and self.specific_fr:
            return self.common_fr + " - " + self.specific_fr
        elif self.common_fr:
            return self.common_fr
        else:
            return self.specific_fr

    @property
    def complete_en(self) -> str:
        if self.common_en and self.specific_en:
            return self.common_en + " - " + self.specific_en
        elif self.common_en:
            return self.common_en
        else:
            return self.specific_en
