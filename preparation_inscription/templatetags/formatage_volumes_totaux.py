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

from ddd.logic.preparation_programme_annuel_etudiant.dtos import UniteEnseignementDTO, UniteEnseignementContenueDTO

register = template.Library()


def formater_volumes(volume_annuel_pm: int = 0, volume_annuel_pp: int = 0) -> str:
    return "{}{}{}".format(
        "{}".format("{}h".format(volume_annuel_pm) if est_un_volume_significatif(volume_annuel_pm) else ''),
        " + " if est_un_volume_significatif(volume_annuel_pm) and est_un_volume_significatif(volume_annuel_pp) else '',
        "{}".format(
            "{}h".format(volume_annuel_pp) if est_un_volume_significatif(volume_annuel_pp) else ''
        )
    )


def est_un_volume_significatif(volume: int) -> bool:
    return volume and volume > 0


@register.filter
def formater_volumes_totaux(unite_catalogue_dto: Union['UniteEnseignementDTO', 'UniteEnseignementContenueDTO']) -> str:
    return formater_volumes(unite_catalogue_dto.volume_annuel_pm, unite_catalogue_dto.volume_annuel_pp)
