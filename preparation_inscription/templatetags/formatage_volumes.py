##############################################################################
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
##############################################################################
from decimal import Decimal
from typing import Optional

from django import template

from ddd.logic.preparation_programme_annuel_etudiant.dtos import UniteEnseignementCatalogueDTO

register = template.Library()


@register.filter
def formater_volumes_totaux(unite_catalogue_dto: 'UniteEnseignementCatalogueDTO') -> str:
    return "%(total_lecturing)gh + %(total_practical)gh" % {
        "total_lecturing": unite_catalogue_dto.volume_annuel_pm or Decimal(0.0),
        "total_practical": unite_catalogue_dto.volume_annuel_pp or Decimal(0.0)
    }


@register.simple_tag
def formater_volumes(volume_annuel_pm: Optional[int], volume_annuel_pp: Optional[int]) -> str:
    return '{}{}{}'.format(
        volume_annuel_pm or '',
        '+' if volume_annuel_pm and volume_annuel_pp else '',
        volume_annuel_pp or ''
    )
