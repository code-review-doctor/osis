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
from typing import List, Optional, Set

from django.db.models import CharField, Q, OuterRef, Case, When, F, DateField, Value, BooleanField, \
    Subquery
from django.db.models.functions import Concat, Coalesce, Cast, Replace

from base.models.enums.exam_enrollment_justification_type import JustificationTypes
from base.models.exam_enrollment import ExamEnrollment
from base.models.session_exam_deadline import SessionExamDeadline
from ddd.logic.encodage_des_notes.encodage.builder.note_etudiant_builder import NoteEtudiantBuilder
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant, NoteEtudiant
from ddd.logic.encodage_des_notes.encodage.dtos import NoteEtudiantFromRepositoryDTO
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from education_group.models.enums.cohort_name import CohortName
from osis_common.ddd.interface import ApplicationService


class NoteEtudiantRepository(INoteEtudiantRepository):

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteNoteEtudiant']] = None,
            codes_unite_enseignement: List[str] = None,
            noms_cohortes: List[str] = None,
            annee_academique: int = None,
            numero_session: int = None,
            nomas: List[str] = None,
            note_manquante: bool = False,
            justification: JustificationTypes = None,
            **kwargs
    ) -> List['NoteEtudiant']:
        filter_qs = cls._build_filter(
            entity_ids=entity_ids,
            noms_cohortes=noms_cohortes,
            codes_unite_enseignement=codes_unite_enseignement,
            annee_academique=annee_academique,
            numero_session=numero_session,
            nomas=nomas,
            note_manquante=note_manquante,
            justification=justification
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
                echeance_gestionnaire=row.echeance_gestionnaire,
                numero_session=row.numero_session,
                code_unite_enseignement=row.code_unite_enseignement,
                annee_academique=row.annee_academique,
                note_decimale_autorisee=row.note_decimale_autorisee,
                nom_cohorte=row.nom_cohorte
            )
            result.append(NoteEtudiantBuilder.build_from_repository_dto(dto_object))
        return result

    @classmethod
    def _build_filter(
            cls,
            entity_ids: Optional[List['IdentiteNoteEtudiant']] = None,
            noms_cohortes: List[str] = None,
            annee_academique: int = None,
            numero_session: int = None,
            nomas: List[str] = None,
            code_unite_enseignement: str = None,
            codes_unite_enseignement: List[str] = None,
            note_manquante: bool = False,
            justification: JustificationTypes = None,
    ) -> List[Q]:
        result = []
        if entity_ids:
            result.append(
                functools.reduce(
                    operator.or_,
                    [
                        Q(
                            code_unite_enseignement=entity_id.code_unite_enseignement,
                            annee_academique=entity_id.annee_academique,
                            numero_session=entity_id.numero_session,
                            noma=entity_id.noma
                        )
                        for entity_id in entity_ids
                    ]
                )
            )
        if nomas:
            result.append(
                Q(noma__in=nomas)
            )
        if noms_cohortes:
            result.append(
                Q(nom_cohorte__in=noms_cohortes)
            )
        if note_manquante:
            result.append(
                Q(note="")
            )
        if justification:
            result.append(
                Q(note=justification.name)
            )
        if annee_academique:
            result.append(
                Q(annee_academique=annee_academique)
            )
        if numero_session:
            result.append(
                Q(numero_session=numero_session)
            )
        if code_unite_enseignement:
            result.append(
                Q(code_unite_enseignement__icontains=code_unite_enseignement)
            )
        if codes_unite_enseignement:
            result.append(
                Q(code_unite_enseignement__in=codes_unite_enseignement)
            )
        return result

    @classmethod
    def search_notes_identites(
            cls,
            noms_cohortes: List[str] = None,
            annee_academique: int = None,
            numero_session: int = None,
            nomas: List[str] = None,
            code_unite_enseignement: str = None,
            enseignant: str = None,
            note_manquante: bool = False,
            **kwargs
    ) -> Set['IdentiteNoteEtudiant']:
        qs = ExamEnrollment.objects.all()

        if annee_academique:
            qs = qs.filter(learning_unit_enrollment__learning_unit_year__academic_year__year=annee_academique)
        if numero_session:
            qs = qs.filter(session_exam__number_session=numero_session)
        if noms_cohortes:
            # qs = qs.filter(learning_unit_enrollment__offer_enrollment__education_group_year__acronym__in=noms_cohortes)
            qs = qs.annotate(
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
            ).filter(nom_cohorte__in=noms_cohortes)
            # cohortes_11ba = {nom for nom in noms_cohortes if '11BA' in nom}
            # cohortes_1ba = {nom for nom in noms_cohortes if '11BA' not in nom}
            # if cohortes_1ba and cohortes_11ba:
            #     equivalent_1ba = {nom.replace('11BA', '1BA') for nom in cohortes_11ba}
            #     cohort_ids = CohortYear.objects.filter(
            #         education_group_year__acronym__in=equivalent_1ba
            #     ).values_list('pk', flat=True).distinct()
            #     qs = qs.filter(
            #         Q(learning_unit_enrollment__offer_enrollment__education_group_year__acronym__in=cohortes_1ba)
            #         | Q(learning_unit_enrollment__offer_enrollment__cohort_year_id__in=cohort_ids)
            #     )
            # elif cohortes_1ba:
            #     qs = qs.filter(learning_unit_enrollment__offer_enrollment__education_group_year__acronym__in=cohortes_1ba)
            # elif cohortes_11ba:
            #     equivalent_1ba = {nom.replace('11BA', '1BA') for nom in cohortes_11ba}
            #     cohort_ids = CohortYear.objects.filter(
            #         education_group_year__acronym__in=equivalent_1ba
            #     ).values_list('pk', flat=True).distinct()
            #     qs = qs.filter(learning_unit_enrollment__offer_enrollment__cohort_year_id__in=cohort_ids)
            # if cohortes_11ba:
            #     equivalent_1ba = {nom.replace('11BA', '1BA') for nom in cohortes_11ba}
            #     qs = qs.filter(learning_unit_enrollment__offer_enrollment__cohort_year__education_group_year__acronym__in=equivalent_1ba)
        if nomas:
            qs = qs.filter(learning_unit_enrollment__offer_enrollment__student__registration_id__in=nomas)
        if note_manquante:
            qs = qs.filter(score_final__isnull=True, justification_final_isnull=True)

        qs = qs.annotate(
            code_unite_enseignement=Concat(
                'learning_unit_enrollment__learning_unit_year__acronym',
                'learning_unit_enrollment__learning_class_year__acronym',
                output_field=CharField()
            ),
        )
        if code_unite_enseignement:
            qs = qs.filter(code_unite_enseignement__icontains=code_unite_enseignement)

        qs = qs.annotate(
            annee_academique=F('learning_unit_enrollment__learning_unit_year__academic_year__year'),
            numero_session=F('session_exam__number_session'),
            noma=F('learning_unit_enrollment__offer_enrollment__student__registration_id'),
        ).values(
            'noma',
            'code_unite_enseignement',
            'annee_academique',
            'numero_session',
        )

        # TODO: Remove filtering to enseignement and use translator to get all code_unite_enseignement + annee_academic
        # managed by tutor name searched
        if enseignant:
            qs = qs.filter(
                Q(learning_unit_enrollment__learning_unit_year__learningcomponentyear__attributionchargenew__attribution__tutor__person__first_name__icontains=enseignant)
                | Q(learning_unit_enrollment__learning_unit_year__learningcomponentyear__attributionchargenew__attribution__tutor__person__last_name__icontains=enseignant)
            )

        return {IdentiteNoteEtudiant(**row) for row in qs}

    @classmethod
    def delete(cls, entity_id: 'IdentiteNoteEtudiant', **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    def save(cls, entity: 'NoteEtudiant') -> None:
        _save_note(entity)

    @classmethod
    def get_all_identities(cls) -> List['IdentiteNoteEtudiant']:
        pass

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
        learning_unit_enrollment__learning_unit_year__academic_year__year=note.annee_academique,
        session_exam__number_session=note.numero_session,
        learning_unit_enrollment__offer_enrollment__student__registration_id=note.entity_id.noma
    )

    db_obj.score_final = note.note.value if note.is_chiffree else None
    db_obj.justification_final = note.note.value.name if note.is_justification else None

    db_obj.save()


def _fetch_session_exams():
    subqs_deadline = SessionExamDeadline.objects.filter(
        number_session=OuterRef("session_exam__number_session"),
        offer_enrollment=OuterRef('learning_unit_enrollment__offer_enrollment')
    ).values('deadline')
    return ExamEnrollment.objects.annotate(
        code_unite_enseignement=Concat(
            'learning_unit_enrollment__learning_unit_year__acronym',
            'learning_unit_enrollment__learning_class_year__acronym',
            output_field=CharField()
        ),
        annee_academique=F('learning_unit_enrollment__learning_unit_year__academic_year__year'),
        numero_session=F('session_exam__number_session'),
        note_decimale_autorisee=Case(
            When(learning_unit_enrollment__learning_unit_year__credits__gte=15, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ),
        noma=F('learning_unit_enrollment__offer_enrollment__student__registration_id'),
        email=F('learning_unit_enrollment__offer_enrollment__student__person__email'),
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
        note=Coalesce(
            'justification_final',
            Cast('score_final', output_field=CharField()),
            'justification_reencoded',
            Cast('score_reencoded', output_field=CharField()),
            'justification_draft',
            Cast('score_draft', output_field=CharField()),
            Value(''),
        ),
        echeance_gestionnaire=Subquery(
            subqs_deadline[:1],
            output_field=DateField()
        )
    ).values_list(
        'code_unite_enseignement',
        'nom_cohorte',
        'annee_academique',
        'numero_session',
        'note_decimale_autorisee',
        'noma',
        'email',
        'note',
        'echeance_gestionnaire',
        named=True
    ).order_by(
        'code_unite_enseignement',
        'nom_cohorte',
        'annee_academique',
        'numero_session',
    )
