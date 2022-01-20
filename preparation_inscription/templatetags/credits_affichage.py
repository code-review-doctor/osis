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
from django import template
from django.utils.translation import gettext_lazy as _

from ddd.logic.preparation_programme_annuel_etudiant.dtos import UniteEnseignementCatalogueDTO, GroupementCatalogueDTO

register = template.Library()


@register.filter
def credits_pour_ue(groupement_contenant: 'UniteEnseignementCatalogueDTO')-> str:
    if groupement_contenant and (groupement_contenant.credits_absolus or groupement_contenant.credits_relatifs):
        return "({} {})".format(
            groupement_contenant.credits_absolus.normalize() or groupement_contenant.credits_relatifs.normalize() or 0,
            _("credits")
        )
    return ""


@register.filter
def credits_pour_groupement(groupement_contenant: 'GroupementCatalogueDTO') -> str:
    if groupement_contenant and groupement_contenant.credits:
        return "({} {})".format(
            groupement_contenant.credits or 0,
            _("credits")
        )
    return ""
