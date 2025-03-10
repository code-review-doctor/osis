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

from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_periode_encodage_notes import \
    IPeriodeEncodageNotesTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import DateDTO, PeriodeEncodageNotesDTO


class PeriodeEncodageNotesTranslatorInMemory(IPeriodeEncodageNotesTranslator):

    periode_soumission_ouverte = PeriodeEncodageNotesDTO(
        annee_concernee=2020,
        session_concernee=2,
        debut_periode_soumission=DateDTO(jour=1, mois=1, annee=datetime.date.today().year),
        fin_periode_soumission=DateDTO(jour=31, mois=12, annee=datetime.date.today().year),
    )
    prochaine_periode_soumission_ouverte = PeriodeEncodageNotesDTO(
        annee_concernee=2020,
        session_concernee=3,
        debut_periode_soumission=DateDTO(jour=1, mois=7, annee=datetime.date.today().year),
        fin_periode_soumission=DateDTO(jour=31, mois=12, annee=datetime.date.today().year),
    )

    @classmethod
    def get(cls) -> 'PeriodeEncodageNotesDTO':
        return cls.periode_soumission_ouverte

    @classmethod
    def get_prochaine_periode(cls) -> 'PeriodeEncodageNotesDTO':
        return cls.prochaine_periode_soumission_ouverte
