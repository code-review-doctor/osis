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
from django import template
from django.utils.translation import gettext_lazy as _

from ddd.logic.preparation_programme_annuel_etudiant.dtos import UniteEnseignementCatalogueDTO

register = template.Library()


@register.filter
def formater_credits_ue(unite_enseignement: 'UniteEnseignementCatalogueDTO') -> str:
    if unite_enseignement and (unite_enseignement.credits_absolus or unite_enseignement.credits_relatifs):
        credits_absolus = unite_enseignement.credits_absolus.normalize() if unite_enseignement.credits_absolus else None
        return "({} {})".format(
            unite_enseignement.credits_relatifs or credits_absolus or 0,
            _("credits")
        )
    return ""


@register.filter
def formater_credits_groupement(credits: Decimal) -> str:
    if credits:
        return "({} {})".format(
            credits or 0,
            _("credits")
        )
    return ""
