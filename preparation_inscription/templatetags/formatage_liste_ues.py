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
from typing import Union

from django import template

from ddd.logic.preparation_programme_annuel_etudiant.dtos import UniteEnseignementContenueDTO, UniteEnseignementDTO
from preparation_inscription.templatetags.formatage_volumes_totaux import formater_volumes
from preparation_inscription.utils.chiffres_significatifs_de_decimal import get_chiffres_significatifs

register = template.Library()


@register.filter
def formatage_credits(unite_catalogue_dto: Union['UniteEnseignementDTO', 'UniteEnseignementContenueDTO']) -> str:
    if unite_catalogue_dto.credits_relatifs:
        if unite_catalogue_dto.credits_relatifs != unite_catalogue_dto.credits_absolus:
            return "{}({})".format(
                unite_catalogue_dto.credits_relatifs,
                get_chiffres_significatifs(unite_catalogue_dto.credits_absolus)
            )
        return "{}".format(unite_catalogue_dto.credits_relatifs)
    return get_chiffres_significatifs(unite_catalogue_dto.credits_absolus)


@register.filter
def formater_volumes_totaux(unite_catalogue_dto: Union['UniteEnseignementDTO', 'UniteEnseignementContenueDTO']) -> str:
    return formater_volumes(unite_catalogue_dto.volume_annuel_pm, unite_catalogue_dto.volume_annuel_pp)
