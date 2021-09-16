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
import functools
import operator
from typing import Optional, List, Dict, Set

from django.db import connection
from django.db.models import F, Case, CharField, Value, When, BooleanField, ExpressionWrapper, DateField, Q, OuterRef, \
    Subquery
from django.db.models.functions import Coalesce, Cast, Concat, Replace

from base.models.exam_enrollment import ExamEnrollment
from base.models.session_exam_deadline import SessionExamDeadline
from ddd.logic.encodage_des_notes.soumission.builder.note_etudiant_builder import NoteEtudiantBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import NoteEtudiant, IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.soumission.dtos import NoteEtudiantFromRepositoryDTO, \
    DateEcheanceNoteDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository, SearchCriteria
from education_group.models.enums.cohort_name import CohortName
from osis_common.ddd.interface import ApplicationService


class NoteEtudiantRepository(INoteEtudiantRepository):
    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteNoteEtudiant']] = None,
            annee_academique: int = None,
            numero_session: int = None,
            code_unite_enseignement: str = None,
            **kwargs
    ) -> List['NoteEtudiant']:
        filter_qs = cls._build_filter(
            entity_ids=entity_ids,
            annee_academique=annee_academique,
            numero_session=numero_session,
            code_unite_enseignement=code_unite_enseignement,
        )
        if not filter_qs:
            return []

        rows = _fetch_session_exams().filter(*filter_qs)
        result = []
        for row in rows:
            dto_object = NoteEtudiantFromRepositoryDTO(
                noma=row.noma,
                email=row.email,
                note=row.note,
                date_limite_de_remise=row.date_limite_de_remise,
                est_soumise=row.est_soumise,
                numero_session=row.number_session,
                code_unite_enseignement=row.acronym,
                annee_academique=row.year,
                credits_unite_enseignement=row.credits_unite_enseignement,
                nom_cohorte=row.nom_cohorte
            )
            result.append(NoteEtudiantBuilder.build_from_repository_dto(dto_object))
        return result

    @classmethod
    def _build_filter(
            cls,
            entity_ids: Optional[List['IdentiteNoteEtudiant']] = None,
            annee_academique: int = None,
            numero_session: int = None,
            code_unite_enseignement: str = None,
    ) -> List[Q]:
        result = []
        if entity_ids:
            result.append(
                functools.reduce(
                    operator.or_,
                    [
                        Q(
                            acronym=entity_id.code_unite_enseignement,
                            year=entity_id.annee_academique,
                            number_session=entity_id.numero_session,
                            noma=entity_id.noma
                        )
                        for entity_id in entity_ids
                    ]
                )
            )
        if annee_academique:
            result.append(
                Q(year=annee_academique)
            )
        if numero_session:
            result.append(
                Q(number_session=numero_session)
            )
        if code_unite_enseignement:
            result.append(
                Q(acronym__icontains=code_unite_enseignement)
            )
        return result

    @classmethod
    def search_by_code_unite_enseignement_annee_session(cls, criterias: List[SearchCriteria]) -> List['NoteEtudiant']:
        if not criterias:
            return []

        q_filters = functools.reduce(
            operator.or_,
            [
                Q(
                    acronym=criteria[0],
                    year=criteria[1],
                    number_session=criteria[2],
                )
                for criteria in criterias
            ]
        )
        rows = _fetch_session_exams().filter(q_filters)
        result = []
        for row in rows:
            dto_object = NoteEtudiantFromRepositoryDTO(
                noma=row.noma,
                email=row.email,
                note=row.note,
                date_limite_de_remise=row.date_limite_de_remise,
                est_soumise=row.est_soumise,
                numero_session=row.number_session,
                code_unite_enseignement=row.acronym,
                annee_academique=row.year,
                credits_unite_enseignement=row.credits_unite_enseignement,
                nom_cohorte=row.acronym
            )
            result.append(NoteEtudiantBuilder.build_from_repository_dto(dto_object))
        return result

    @classmethod
    def search_dates_echeances(
            cls,
            notes_identites: Set[IdentiteNoteEtudiant]
    ) -> List[DateEcheanceNoteDTO]:
        dates_echeances_dto = []
        if notes_identites:
            parameters = _get_dates_echeances_query_parameters(notes_identites)
            with connection.cursor() as cursor:
                raw_query = '''
                    SELECT 
                        CONCAT(base_learningunityear.acronym, learning_unit_learningclassyear.acronym) AS code_unite_enseignement, 
                        base_academicyear.year AS annee_academique, 
                        base_sessionexam.number_session AS numero_session, 
                        base_student.registration_id AS noma,
                        CASE
                            WHEN score_final IS NOT NULL THEN true
                            WHEN justification_final IS NOT NULL THEN true
                            ELSE false
                        END note_soumise,
                        (
                            SELECT CASE
                                    WHEN deadline_tutor IS NULL THEN deadline
                                    ELSE deadline - deadline_tutor
                                END echeance
                            FROM base_sessionexamdeadline
                            WHERE base_sessionexamdeadline.number_session = base_sessionexam.number_session 
                                  and base_sessionexamdeadline.offer_enrollment_id = base_learningunitenrollment.offer_enrollment_id
                            LIMIT 1
                        ) AS echeance
                    FROM base_examenrollment
                    JOIN base_learningunitenrollment on base_learningunitenrollment.id = base_examenrollment.learning_unit_enrollment_id
                    JOIN base_learningunityear on base_learningunityear.id = base_learningunitenrollment.learning_unit_year_id
                    LEFT JOIN learning_unit_learningclassyear on learning_unit_learningclassyear.id = base_learningunitenrollment.learning_class_year_id
                    JOIN base_academicyear on base_academicyear.id = base_learningunityear.academic_year_id
                    JOIN base_sessionexam on base_sessionexam.id = base_examenrollment.session_exam_id       
                    JOIN base_offerenrollment on base_offerenrollment.id = base_learningunitenrollment.offer_enrollment_id
                    JOIN base_student on base_student.id = base_offerenrollment.student_id            
                    WHERE base_academicyear.year = %(academic_year)s AND
                        base_sessionexam.number_session = %(number_session)s  AND 
                        base_student.registration_id in %(registration_ids)s AND
                        CONCAT(base_learningunityear.acronym, learning_unit_learningclassyear.acronym) in %(acronyms)s     
                    ORDER BY code_unite_enseignement, annee_academique, echeance
                '''
                cursor.execute(raw_query, parameters)
                for row in cursor.fetchall():
                    dates_echeances_dto.append(
                        DateEcheanceNoteDTO(
                            code_unite_enseignement=row[0],
                            annee_unite_enseignement=row[1],
                            numero_session=row[2],
                            noma=row[3],
                            note_soumise=row[4],
                            jour=row[5].day,
                            mois=row[5].month,
                            annee=row[5].year,
                        )
                    )
        return dates_echeances_dto

    @classmethod
    def delete(cls, entity_id: 'IdentiteNoteEtudiant', **kwargs: ApplicationService) -> None:
        raise NotImplementedError

    @classmethod
    def save(cls, entity: 'NoteEtudiant') -> None:
        _save_note(entity)

    @classmethod
    def get_all_identities(cls) -> List['IdentiteNoteEtudiant']:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'IdentiteNoteEtudiant') -> 'NoteEtudiant':
        return cls.search([entity_id])[0]


def _save_note(note: 'NoteEtudiant'):
    db_obj = ExamEnrollment.objects.annotate(
        code_unite_enseignement=Concat(
            'learning_unit_enrollment__learning_unit_year__acronym',
            'learning_unit_enrollment__learning_class_year__acronym',
            output_field=CharField()
        )
    ).get(
        code_unite_enseignement=note.code_unite_enseignement,
        learning_unit_enrollment__learning_unit_year__academic_year__year=note.annee,
        session_exam__number_session=note.numero_session,
        learning_unit_enrollment__offer_enrollment__student__registration_id=note.entity_id.noma
    )
    if note.est_soumise:
        db_obj.score_final = note.note.value if note.is_chiffree else None
        db_obj.justification_final = note.note.value.name if note.is_justification else None
    else:
        db_obj.score_draft = note.note.value if note.is_chiffree else None
        db_obj.justification_draft = note.note.value.name if note.is_justification else None

    db_obj.save()


def _fetch_session_exams():
    subqs_deadline = SessionExamDeadline.objects.filter(
        number_session=OuterRef("session_exam__number_session"),
        offer_enrollment=OuterRef('learning_unit_enrollment__offer_enrollment')
    ).annotate(
        date_limite_de_remise=Case(
            When(deadline_tutor__isnull=True, then=F('deadline')),
            default=ExpressionWrapper(F('deadline') - F('deadline_tutor'), output_field=DateField())
        )
    ).values('date_limite_de_remise')
    return ExamEnrollment.objects.annotate(
        acronym=Concat(
            'learning_unit_enrollment__learning_unit_year__acronym',
            'learning_unit_enrollment__learning_class_year__acronym',
            output_field=CharField()
        ),
        year=F('learning_unit_enrollment__learning_unit_year__academic_year__year'),
        number_session=F('session_exam__number_session'),
        credits_unite_enseignement=F('learning_unit_enrollment__learning_unit_year__credits'),
        noma=F('learning_unit_enrollment__offer_enrollment__student__registration_id'),
        email=F('learning_unit_enrollment__offer_enrollment__student__person__email'),
        note=Coalesce(
            'justification_final',
            Cast('score_final', output_field=CharField()),
            'justification_reencoded',
            Cast('score_reencoded', output_field=CharField()),
            'justification_draft',
            Cast('score_draft', output_field=CharField()),
            Value(''),
        ),
        est_soumise=Case(
            When(score_final__isnull=False, then=Value(True)),
            When(justification_final__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ),
        date_limite_de_remise=Subquery(
            subqs_deadline[:1],
            output_field=DateField()
        ),
        nom_cohorte=Case(
            When(
                learning_unit_enrollment__offer_enrollment__cohort_year__name=CohortName.FIRST_YEAR.name,
                then=Replace(
                    'learning_unit_enrollment__offer_enrollment__education_group_year__acronym',
                    Value('1BA'),
                    Value('11BA')
                )
            ),
            default=F('learning_unit_enrollment__offer_enrollment__education_group_year__acronym'),
            output_field=CharField()
        ),
    ).values_list(
        'acronym',
        'year',
        'number_session',
        'nom_cohorte',
        'credits_unite_enseignement',
        'noma',
        'email',
        'note',
        'date_limite_de_remise',
        'est_soumise',
        named=True
    ).order_by(
        'acronym',
        'year',
        'number_session',
    )


def _get_dates_echeances_query_parameters(notes_identites: Set[IdentiteNoteEtudiant]) -> Dict:
    acronyms = set()
    registration_ids = set()
    academic_year = None
    number_session = None

    for note_identite in notes_identites:
        acronyms.add(note_identite.code_unite_enseignement)
        registration_ids.add(note_identite.noma)
        academic_year = note_identite.annee_academique
        number_session = note_identite.numero_session

    return {
        "acronyms": tuple(acronyms),
        "academic_year": academic_year,
        "number_session": number_session,
        "registration_ids": tuple(registration_ids),
    }
