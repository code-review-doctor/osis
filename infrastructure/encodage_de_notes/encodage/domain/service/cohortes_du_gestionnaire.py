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

from django.db.models import Subquery, OuterRef, F

from base.auth.roles.program_manager import ProgramManager
from base.models.education_group_year import EducationGroupYear
from ddd.logic.encodage_des_notes.encodage.domain.service.i_cohortes_du_gestionnaire import ICohortesDuGestionnaire
from ddd.logic.encodage_des_notes.encodage.dtos import CohorteGestionnaireDTO


class CohortesDuGestionnaireTranslator(ICohortesDuGestionnaire):

    @classmethod
    def search(
            cls,
            matricule_gestionnaire: str,
    ) -> Set['CohorteGestionnaireDTO']:
        qs = ProgramManager.objects.filter(
            person__global_id=matricule_gestionnaire
        ).annotate(
            nom_formation=Subquery(
                EducationGroupYear.objects.filter(
                    education_group_id=OuterRef('education_group_id')
                ).order_by(
                    '-academic_year__year'
                ).values('acronym')[:1]
            ),
            matricule_gestionnaire=F('person__global_id'),
            is_11ba=F('cohort'),
        ).values(
            'nom_formation',
            'is_11ba',
            'matricule_gestionnaire',
        )
        result = set()
        for values_dict in qs:
            nom_cohorte = values_dict['nom_formation']
            if values_dict['is_11ba']:
                nom_cohorte = nom_cohorte.replace('1BA', '11BA')
            result.add(
                CohorteGestionnaireDTO(
                    matricule_gestionnaire=values_dict['matricule_gestionnaire'],
                    nom_cohorte=nom_cohorte,
                )
            )
        return result
