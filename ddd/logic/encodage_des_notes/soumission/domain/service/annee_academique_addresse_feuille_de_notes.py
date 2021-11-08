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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
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
from ddd.logic.shared_kernel.academic_year.domain.service.get_current_academic_year import GetCurrentAcademicYear
from ddd.logic.shared_kernel.academic_year.repository.i_academic_year import IAcademicYearRepository
from osis_common.ddd import interface


# FIXME :: à ssupprimer ? Il n'est pas possible d'appeler ce service en dehors de la periode encodage de notes => le AcademicYearRepo est inutile
class AnneeAcademiqueAddresseFeuilleDeNotesDomaineService(interface.DomainService):
    @classmethod
    def get(
            cls,
            periode_soumission_note_translator: 'IPeriodeEncodageNotesTranslator',
            academic_year_repo: 'IAcademicYearRepository'
    ) -> int:
        periode_soumission = periode_soumission_note_translator.get()
        if periode_soumission:
            return periode_soumission.annee_concernee

        return GetCurrentAcademicYear().get_starting_academic_year(
            datetime.date.today(),
            academic_year_repo
        ).year
