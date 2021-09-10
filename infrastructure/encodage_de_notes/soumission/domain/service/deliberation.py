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
from typing import Set

from django.db.models import F, Case, When, Value, CharField
from django.db.models.functions import Replace

from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from base.models.offer_year_calendar import OfferYearCalendar
from ddd.logic.encodage_des_notes.soumission.domain.service.i_deliberation import IDeliberationTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import DeliberationDTO, DateDTO
from education_group.models.enums.cohort_name import CohortName


class DeliberationTranslator(IDeliberationTranslator):

    @classmethod
    def search(
            cls,
            annee: int,
            session: int,
            noms_cohortes: Set[str],
    ) -> Set['DeliberationDTO']:
        qs = OfferYearCalendar.objects.filter(
            academic_calendar__reference=AcademicCalendarTypes.DELIBERATION.name,
            education_group_year__academic_year__year=annee,
            academic_calendar__sessionexamcalendar__number_session=session,
        ).annotate(
            date=F('start_date'),
            nom_cohorte=Case(
                When(
                    cohort_year__name=CohortName.FIRST_YEAR.name,
                    then=Replace('education_group_year__acronym', Value('1BA'), Value('11BA'))
                ),
                default=F('education_group_year__acronym'),
                output_field=CharField()
            ),
        ).filter(
            nom_cohorte__in=noms_cohortes
        ).values(
            'date',
            'nom_cohorte',
        ).distinct()
        deliberation_dtos = set()
        for values in qs:
            datetime_delibe = values['date']
            deliberation_dtos.add(
                DeliberationDTO(
                    annee=annee,
                    session=session,
                    nom_cohorte=values['nom_cohorte'],
                    date=DateDTO(jour=datetime_delibe.day, mois=datetime_delibe.month, annee=datetime_delibe.year)
                    if datetime_delibe else None,
                )
            )
        return deliberation_dtos
