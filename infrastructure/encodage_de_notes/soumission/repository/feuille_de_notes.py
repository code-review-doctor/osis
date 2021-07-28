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
import itertools
import operator
from typing import Optional, List

from django.db.models import F, Case, CharField, Value, When, BooleanField, ExpressionWrapper, DateField, Q, Subquery, \
    OuterRef
from django.db.models.functions import Coalesce, Cast, Concat

from base.models.exam_enrollment import ExamEnrollment
from base.models.session_exam_deadline import SessionExamDeadline
from ddd.logic.encodage_des_notes.soumission.builder.feuille_de_notes_builder import FeuilleDeNotesBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model._note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import IdentiteFeuilleDeNotes, FeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import FeuilleDeNotesFromRepositoryDTO, NoteEtudiantFromRepositoryDTO
from ddd.logic.encodage_des_notes.soumission.repository.i_feuille_de_notes import IFeuilleDeNotesRepository
from osis_common.ddd.interface import ApplicationService


class FeuilleDeNotesRepository(IFeuilleDeNotesRepository):
    @classmethod
    def search(cls, entity_ids: Optional[List['IdentiteFeuilleDeNotes']] = None, **kwargs) -> List['FeuilleDeNotes']:
        if not entity_ids:
            return []

        q_filters = functools.reduce(
            operator.or_,
            [
                Q(
                    acronym=entity_id.code_unite_enseignement,
                    year=entity_id.annee_academique,
                    number_session=entity_id.numero_session
                )
                for entity_id in entity_ids
            ]
        )
        rows = _fetch_session_exams().filter(q_filters)
        rows_group_by_identity = itertools.groupby(rows, key=lambda row: (row.acronym, row.year, row.number_session))

        result = []
        for identity, group_rows in rows_group_by_identity:
            group_rows = list(group_rows)
            dto_object = FeuilleDeNotesFromRepositoryDTO(
                numero_session=identity[2],
                code_unite_enseignement=identity[0],
                annee_academique=identity[1],
                credits_unite_enseignement=float(group_rows[0].credits_unite_enseignement),
                notes=set(
                    NoteEtudiantFromRepositoryDTO(
                        noma=row.noma,
                        email=row.email,
                        note=row.note,
                        date_limite_de_remise=row.date_limite_de_remise,
                        est_soumise=row.est_soumise
                    )
                    for row in group_rows
                )
            )
            result.append(FeuilleDeNotesBuilder().build_from_repository_dto(dto_object))
        return result

    @classmethod
    def delete(cls, entity_id: 'IdentiteFeuilleDeNotes', **kwargs: ApplicationService) -> None:
        raise NotImplementedError

    @classmethod
    def save(cls, entity: 'FeuilleDeNotes') -> None:
        for note in entity.notes:
            _save_note(entity.entity_id, note)

    @classmethod
    def get_all_identities(cls) -> List['IdentiteFeuilleDeNotes']:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'IdentiteFeuilleDeNotes') -> 'FeuilleDeNotes':
        return cls.search([entity_id])[0]

    @classmethod
    def get_progression_generale(cls, entity_ids: List['IdentiteFeuilleDeNotes']) -> 'ProgressionGeneraleEncodageNotesDTO':
        session_concernee = entity_ids[0].numero_session
        q_filters = functools.reduce(
            operator.or_,
            [
                Q(
                    learning_unit_enrollment__learning_unit_year__acronym=entity_id.code_unite_enseignement,
                    learning_unit_enrollment__learning_unit_year__academic_year__year=entity_id.annee_academique,
                )
                for entity_id in entity_ids
            ]
        )
        ExamEnrollment.objects.filter(
            # Une seule période d'encodage de notes ouverte à un même moment
            session_exam__number_session=session_concernee,
        ).filter(
            q_filters
        ).annotate(
            code_unite_enseignement=F('learning_unit_enrollment__learning_unit_year__acronym'),
            # intitule_complet_unite_enseignement=Subquery(
            #     LearningUnitYear.objects.filter(
            #         pk=OuterRef('learning_unit_enrollment__learning_unit_year__pk'),
            #     ).annotate_full_title().values('full_title')[:1],
            #     output_field=CharField()
            # ),
            date_echeance=Subquery(
                SessionExamDeadline.objects.filter(
                    offer_enrollment=OuterRef('offer_enrollment'),
                    session=OuterRef('session_exam__number_session'),
                ).values('deadline_tutor')[:1],
                output_field=DateField()
            ),

        )
        # subquery_notes_soumises = Subquery(
        #     ExamEnrollment.objects.filter(
        #         learning_unit_enrollment__offer_enrollment__sessionexamdeadline__deadline=OuterRef('deadline'),
        #         learning_unit_enrollment__offer_enrollment__sessionexamdeadline__deadline_tutor=OuterRef('deadline_tutor'),
        #         learning_unit_enrollment__learning_unit_year__acronym=OuterRef('code_unite_enseignement'),
        #         learning_unit_enrollment__learning_unit_year__academic_year__year=OuterRef('annee_unite_enseignement'),
        #     ).filter(
        #         Q(score_final__isnull=False) | Q(justification_final__isnull=False)
        #     ).values(
        #
        #     ).annotate(
        #         count=Count('pk'),
        #     ).values(
        #         'count'
        #     ),
        #     output_field=IntegerField(),
        # )
        # subquery_notes_total = Subquery(
        #     ExamEnrollment.objects.filter(
        #         learning_unit_enrollment__offer_enrollment__sessionexamdeadline__deadline=OuterRef('deadline'),
        #         learning_unit_enrollment__offer_enrollment__sessionexamdeadline__deadline_tutor=OuterRef('deadline_tutor'),
        #         learning_unit_enrollment__learning_unit_year__acronym=OuterRef('code_unite_enseignement'),
        #         learning_unit_enrollment__learning_unit_year__academic_year__year=OuterRef('annee_unite_enseignement'),
        #     ).annotate(
        #         count=Count('pk'),
        #     ).values(
        #         'count'
        #     ),
        #     output_field=IntegerField(),
        # )

        # qs = SessionExamDeadline.objects.filter(
        #     # Une seule période d'encodage de notes ouverte à un même moment
        #     number_session=entity_ids[0].numero_session,
        # ).filter(
        #     q_filters
        # ).annotate(
        #     code_unite_enseignement=F('offer_enrollment__learningunitenrollment__learning_unit_year__acronym'),
        #     annee_unite_enseignement=F('offer_enrollment__learningunitenrollment__learning_unit_year__academic_year__year'),
        # ).values(
        #     # 'pk',
        #     # 'date_limite_de_remise',
        #     'deadline_tutor',
        #     'deadline',
        #     'code_unite_enseignement',
        #     'annee_unite_enseignement',
        # ).distinct(
        #
        # ).annotate(
        #     quantite_notes_soumises=Coalesce(subquery_notes_soumises, 0),
        #     quantite_total_notes=Coalesce(subquery_notes_total, 0),
        #     date_limite_de_remise=Case(
        #         When(
        #             deadline_tutor__isnull=True,
        #             then='deadline'
        #         ),
        #         default=ExpressionWrapper(
        #             F('deadline') -
        #             F('deadline_tutor'),
        #             output_field=DateField()
        #         )
        #     ),
        # ).values(
        #     'quantite_notes_soumises',
        #     'quantite_total_notes',
        #     'date_limite_de_remise',
        # )
        print(str(qs))
        print()
        print()



def _save_note(feuille_de_note_entity_id: 'IdentiteFeuilleDeNotes', note: 'NoteEtudiant'):
    db_obj = ExamEnrollment.objects.annotate(
        code_unite_enseignement=Concat(
            'learning_unit_enrollment__learning_unit_year__acronym',
            'learning_unit_enrollment__learning_class_year__acronym',
            output_field=CharField()
        )
    ).get(
        code_unite_enseignement=feuille_de_note_entity_id.code_unite_enseignement,
        learning_unit_enrollment__learning_unit_year__academic_year__year=feuille_de_note_entity_id.annee_academique,
        session_exam__number_session=feuille_de_note_entity_id.numero_session,
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
        date_limite_de_remise=Case(
            When(
                learning_unit_enrollment__offer_enrollment__sessionexamdeadline__deadline_tutor__isnull=True,
                then=F('learning_unit_enrollment__offer_enrollment__sessionexamdeadline__deadline')
            ),
            default=ExpressionWrapper(
                F('learning_unit_enrollment__offer_enrollment__sessionexamdeadline__deadline') -
                F('learning_unit_enrollment__offer_enrollment__sessionexamdeadline__deadline_tutor'),
                output_field=DateField()
            )
        ),
        est_soumise=Case(
            When(score_final__isnull=False, then=Value(True)),
            When(justification_final__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).values_list(
        'acronym',
        'year',
        'number_session',
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
