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
import datetime

from assessments.calendar.scores_exam_submission_calendar import ScoresExamSubmissionCalendar
from ddd.logic.encodage_des_notes.shared_kernel.domain.service import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import DateDTO, PeriodeEncodageNotesDTO


class PeriodeEncodageNotesTranslator(IPeriodeEncodageNotesTranslator):

    @classmethod
    def get(cls) -> 'PeriodeEncodageNotesDTO':
        calendar = ScoresExamSubmissionCalendar()
        events = calendar.get_opened_academic_events(date=datetime.date.today())
        if events:
            event = events[0]
            date_debut = event.start_date
            date_fin = event.end_date
            return PeriodeEncodageNotesDTO(
                annee_concernee=event.authorized_target_year,
                session_concernee=event.session,
                debut_periode_soumission=DateDTO(jour=date_debut.day, mois=date_debut.month, annee=date_debut.year),
                fin_periode_soumission=DateDTO(jour=date_fin.day, mois=date_fin.month, annee=date_fin.year),
            )
