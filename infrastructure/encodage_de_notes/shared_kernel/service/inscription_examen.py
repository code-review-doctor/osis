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

from django.db.models import F, Case, When, QuerySet, Value, CharField
from django.db.models.functions import Concat, Replace

from base.models.enums import exam_enrollment_state
from base.models.enums.component_type import PRACTICAL_EXERCISES
from base.models.enums.learning_component_year_type import LECTURING
from base.models.exam_enrollment import ExamEnrollment
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_inscription_examen import IInscriptionExamenTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import InscriptionExamenDTO, DesinscriptionExamenDTO
from ddd.logic.encodage_des_notes.shared_kernel.dtos import DateDTO


class InscriptionExamenTranslator(IInscriptionExamenTranslator):

    @classmethod
    def search_desinscrits(
            cls,
            code_unite_enseignement: str,
            numero_session: int,
            annee: int
    ) -> Set['DesinscriptionExamenDTO']:
        return cls.search_desinscrits_pour_plusieurs_unites_enseignement(
            {code_unite_enseignement},
            numero_session,
            annee
        )

    @classmethod
    def search_inscrits(
            cls,
            code_unite_enseignement: str,
            numero_session: int,
            annee: int,
    ) -> Set['InscriptionExamenDTO']:
        return cls.search_inscrits_pour_plusieurs_unites_enseignement(
            {code_unite_enseignement},
            numero_session,
            annee,
        )

    @classmethod
    def search_inscrits_pour_plusieurs_unites_enseignement(
            cls,
            codes_unites_enseignement: Set[str],
            numero_session: int,
            annee: int,
    ) -> Set['InscriptionExamenDTO']:
        qs_as_values = _get_common_queryset(
            codes_unites_enseignement=codes_unites_enseignement,
            numero_session=numero_session,
            annee=annee,
        ).filter(
            enrollment_state=exam_enrollment_state.ENROLLED,
        ).annotate(
            annee=F('learning_unit_enrollment__learning_unit_year__academic_year__year'),
            noma=F('learning_unit_enrollment__offer_enrollment__student__registration_id'),
            nom_cohorte=Case(
                When(
                    learning_unit_enrollment__offer_enrollment__cohort_year__isnull=False,
                    then=Replace(
                        'learning_unit_enrollment__offer_enrollment__education_group_year__acronym',
                        Value('1BA'),
                        Value('11BA')
                    ),
                ),
                default='learning_unit_enrollment__offer_enrollment__education_group_year__acronym',
                output_field=CharField(),
            ),
            date_inscription=F('date_enrollment'),
        ).values(
            'annee',
            'noma',
            'code_unite_enseignement',
            'nom_cohorte',
            'date_inscription',
        )
        return {
            InscriptionExamenDTO(
                annee=values['annee'],
                noma=values['noma'],
                code_unite_enseignement=values['code_unite_enseignement'],
                nom_cohorte=values['nom_cohorte'],
                date_inscription=DateDTO.build_from_date(values['date_inscription'])
                if values['date_inscription'] else None
            ) for values in qs_as_values
        }

    @classmethod
    def search_desinscrits_pour_plusieurs_unites_enseignement(
            cls,
            codes_unites_enseignement: Set[str],
            numero_session: int,
            annee: int,
    ) -> Set['DesinscriptionExamenDTO']:
        qs_as_values = _get_common_queryset(
            codes_unites_enseignement=codes_unites_enseignement,
            numero_session=numero_session,
            annee=annee,
        ).exclude(
            enrollment_state=exam_enrollment_state.ENROLLED,
        ).annotate(
            annee=F('learning_unit_enrollment__learning_unit_year__academic_year__year'),
            noma=F('learning_unit_enrollment__offer_enrollment__student__registration_id'),
            nom_cohorte=Case(
                When(
                    learning_unit_enrollment__offer_enrollment__cohort_year__isnull=False,
                    then=Replace(
                        'learning_unit_enrollment__offer_enrollment__education_group_year__acronym',
                        Value('1BA'),
                        Value('11BA')
                    ),
                ),
                default='learning_unit_enrollment__offer_enrollment__education_group_year__acronym',
                output_field=CharField(),
            ),
        ).values(
            'annee',
            'noma',
            'code_unite_enseignement',
            'nom_cohorte',
        )
        return {DesinscriptionExamenDTO(**values) for values in qs_as_values}


def _get_common_queryset(
        codes_unites_enseignement: Set[str],
        numero_session: int,
        annee: int,
) -> QuerySet:
    codes_unites_enseignement_without_class_acronym = {
        code.replace('-', '').replace('_', '')[:-1]
        for code in codes_unites_enseignement
    }
    codes_unites_enseignement_pour_filtre = codes_unites_enseignement_without_class_acronym.union(
        codes_unites_enseignement
    )
    return ExamEnrollment.objects.filter(
        learning_unit_enrollment__learning_unit_year__academic_year__year=annee,
        session_exam__number_session=numero_session,
        learning_unit_enrollment__learning_unit_year__acronym__in=codes_unites_enseignement_pour_filtre
    ).annotate(
        code_unite_enseignement=Case(
            When(
                learning_unit_enrollment__learning_class_year__learning_component_year__type=LECTURING,
                then=Concat(
                    'learning_unit_enrollment__learning_unit_year__acronym',
                    Value('-'),
                    'learning_unit_enrollment__learning_class_year__acronym',
                    output_field=CharField()
                )
            ),
            When(
                learning_unit_enrollment__learning_class_year__learning_component_year__type=PRACTICAL_EXERCISES,
                then=Concat(
                    'learning_unit_enrollment__learning_unit_year__acronym',
                    Value('_'),
                    'learning_unit_enrollment__learning_class_year__acronym',
                    output_field=CharField()
                )
            ),
            default=F('learning_unit_enrollment__learning_unit_year__acronym'),
            output_field=CharField()
        ),
    ).filter(
        code_unite_enseignement__in=codes_unites_enseignement,
    )
