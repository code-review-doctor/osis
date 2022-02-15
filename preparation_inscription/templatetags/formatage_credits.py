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
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

register = template.Library()


def get_chiffres_significatifs(nombre_decimal: Decimal) -> str:
    if nombre_decimal:
        str_volume = str(nombre_decimal)
        return str_volume.rstrip('0').rstrip('.') if '.' in str_volume else str_volume
    return ''


@register.simple_tag
def formater_credits_ue_formulaire(credits_relatifs: Optional[int], credits_absolus: Optional[Decimal]) -> str:
    if credits_absolus or credits_relatifs:
        credits_absolus = get_chiffres_significatifs(credits_absolus) if credits_absolus else None
        return "({} {})".format(credits_relatifs or credits_absolus or 0, _("credits"))
    return ""


@register.simple_tag
def formater_credits_ue(
        credits_relatifs: Optional[int],
        credits_absolus: Optional[Decimal],
        intitule_groupement: str
) -> str:
    if credits_relatifs:
        if credits_relatifs != credits_absolus:
            return mark_safe('<div data-toggle="tooltip" title="{} {} ({})">{}({})</div>'.format(
                _("Program credits"),
                intitule_groupement,
                _("Learning unit credits"),
                credits_relatifs,
                get_chiffres_significatifs(credits_absolus))
            )
        return "{}".format(credits_relatifs)
    return get_chiffres_significatifs(credits_absolus)


@register.filter
def formater_credits_groupement(credits: Decimal) -> str:
    if credits:
        return "({} {})".format(
            credits or 0,
            _("credits")
        )
    return ""
