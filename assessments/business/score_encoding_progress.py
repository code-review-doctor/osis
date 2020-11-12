##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from collections import OrderedDict
from typing import List

import attr
from django.db.models import OuterRef, Subquery, Q, Count, F

from attribution.models import attribution
from base.auth.roles import program_manager
from base.models import offer_year, exam_enrollment, tutor
from base.models.enums import exam_enrollment_state
from base.models.exam_enrollment import ExamEnrollment
from base.models.learning_unit_year import LearningUnitYear
from base.models.offer_year import OfferYear
from base.models.session_exam_deadline import SessionExamDeadline, compute_deadline_tutor
from base.models.tutor import Tutor


def get_scores_encoding_progress(user, offer_year_id, number_session, academic_year, learning_unit_year_ids=None):
    queryset = exam_enrollment.get_progress_by_learning_unit_years_and_offer_years(
        user=user,
        offer_year_id=offer_year_id,
        session_exam_number=number_session,
        academic_year=academic_year,
        learning_unit_year_ids=learning_unit_year_ids,
        only_enrolled=True
    )

    return _sort_by_acronym([ScoreEncodingProgress(obj) for obj in queryset])


def find_related_offer_years(score_encoding_progress_list):
    all_offers_ids = [score_encoding_progress.offer_year_id for score_encoding_progress in score_encoding_progress_list]
    return OfferYear.objects.filter(pk__in=all_offers_ids).order_by('acronym')


def find_related_tutors(user, academic_year, session_exam_number):
    # Find all offer managed by current user
    offer_year_ids = list(offer_year.find_by_user(user).values_list('id', flat=True))

    learning_unit_year_ids = list(exam_enrollment.find_for_score_encodings(session_exam_number=session_exam_number,
                                                                      academic_year=academic_year,
                                                                      offers_year=offer_year_ids,
                                                                      with_session_exam_deadline=False)\
                                            .distinct('learning_unit_enrollment__learning_unit_year')\
                                            .values_list('learning_unit_enrollment__learning_unit_year_id', flat=True))

    tutors = tutor.find_by_learning_unit(learning_unit_year_ids)
    return sorted(tutors, key=_order_by_last_name_and_first_name)


def _order_by_last_name_and_first_name(tutor):
    # Somebody person must be first on list
    SOMEBODY_GID = '99999998'
    if tutor.person.global_id == SOMEBODY_GID:
        return ('_', '_')
    last_name = tutor.person.last_name.lower() if tutor.person.last_name else ""
    first_name = tutor.person.first_name.lower() if tutor.person.first_name else ""
    return (last_name, first_name)


def group_by_learning_unit_year(score_encoding_progress_list):
    scores_encoding_progress_grouped = []
    if score_encoding_progress_list:
        scores_encoding_progress_grouped = _group_by_learning_unit(score_encoding_progress_list)
    return _sort_by_acronym(scores_encoding_progress_grouped)


def append_related_tutors_and_score_responsibles(score_encoding_progress_list):
    tutors_grouped = _get_tutors_grouped_by_learning_unit(score_encoding_progress_list)

    for score_encoding_progress in score_encoding_progress_list:
        tutors_related = tutors_grouped.get(score_encoding_progress.learning_unit_year_id)
        score_encoding_progress.tutors = tutors_related
        score_encoding_progress.score_responsibles = [tutor for tutor in tutors_related if tutor.is_score_responsible]\
                                                      if tutors_related else None

    return score_encoding_progress_list


def filter_only_incomplete(score_encoding_progress_list):
    return [score_encoding_progress for score_encoding_progress in score_encoding_progress_list
            if score_encoding_progress.exam_enrollments_encoded != score_encoding_progress.total_exam_enrollments]


def filter_only_without_attribution(score_encoding_progress_list):
    return [score_encoding_progress for score_encoding_progress in score_encoding_progress_list
            if not score_encoding_progress.tutors]


def _get_tutors_grouped_by_learning_unit(score_encoding_progress_list):
    all_attributions = list(_find_related_attribution(score_encoding_progress_list))
    tutors_grouped_by_learning_unit = {}
    for att in all_attributions:
        tutor = att.tutor
        tutor.is_score_responsible = att.score_responsible
        tutors_grouped_by_learning_unit.setdefault(att.learning_unit_year.id, []).append(tutor)

    return tutors_grouped_by_learning_unit


def _find_related_attribution(score_encoding_progress_list):
    learning_units = [score_encoding_progress.learning_unit_year_id for score_encoding_progress in
                      score_encoding_progress_list]

    return attribution.search(list_learning_unit_year=learning_units)\
                      .order_by('tutor__person__last_name', 'tutor__person__first_name')


def _group_by_learning_unit(score_encoding_progress_list):
    group_by_learning_unit = {}
    for score_encoding_progress in score_encoding_progress_list:
        key = score_encoding_progress.learning_unit_year_id
        if key in group_by_learning_unit:
            score_encoding_progress_to_update = group_by_learning_unit[key]
            score_encoding_progress_to_update.increment_progress(score_encoding_progress)
            score_encoding_progress_to_update.increment_deadlines_count(score_encoding_progress)
        else:
            group_by_learning_unit[key] = score_encoding_progress
    return list(group_by_learning_unit.values())


def _sort_by_acronym(score_encoding_progress_list):
    return sorted(score_encoding_progress_list, key=lambda k: k.learning_unit_year_acronym)


class ScoreEncodingProgress:
    def __init__(self, exam_enrol: exam_enrollment.ExamEnrollment):
        self.learning_unit_year_id = exam_enrol.learning_unit_year_id
        self.learning_unit_year_acronym = exam_enrol.learning_unit_year_acronym
        self.learning_unit_year_title = ' - '.join(
            filter(None,
                   [exam_enrol.learning_container_year_common_title,
                    exam_enrol.learning_unit_year_specific_title]
                   )
        )

        self.offer_year_id = exam_enrol.offer_year_id
        self.exam_enrollments_encoded = exam_enrol.exam_enrollments_encoded
        self.draft_scores = exam_enrol.draft_scores
        self.scores_not_yet_submitted = exam_enrol.scores_not_yet_submitted
        self.total_exam_enrollments = exam_enrol.total_exam_enrollments
        self.deadlines_count = {  # TODO :: to rename and add documentation
            compute_deadline_tutor(exam_enrol.deadline, exam_enrol.deadline_tutor): self.scores_not_yet_submitted
        }
        # self.session_exam_deadlines = sorted(
        #     deadline.computed_deadline for deadline in exam_enrol.session_exam_deadlines
        # )

    @property
    def progress_int(self):
        return (self.exam_enrollments_encoded / self.total_exam_enrollments) * 100

    @property
    def progress(self):
        return "{0:.0f}".format(self.progress_int)

    @property
    def ordered_deadlines_count(self):
        return OrderedDict(sorted(self.deadlines_count.items()))

    def increment_progress(self, score_encoding_progress):
        self.draft_scores += score_encoding_progress.draft_scores
        self.scores_not_yet_submitted += score_encoding_progress.scores_not_yet_submitted
        self.exam_enrollments_encoded += score_encoding_progress.exam_enrollments_encoded
        self.total_exam_enrollments += score_encoding_progress.total_exam_enrollments

    def increment_deadlines_count(self, score_encoding_progress):
        for deadline_computed, scores_not_yet_submitted in score_encoding_progress.deadlines_count.items():
            if deadline_computed in self.deadlines_count:
                self.deadlines_count[deadline_computed] += scores_not_yet_submitted
            else:
                self.deadlines_count[deadline_computed] = scores_not_yet_submitted


@attr.s(slots=True, frozen=True)
class DeadlineScoreEncodingProgress:
    deadline_tutor = attr.ib(type=datetime.datetime)
    exam_enrollments_encoded = attr.ib(type=int)
    scores_not_yet_submitted = attr.ib(type=int)
    total_exam_enrollments = attr.ib(type=int)


@attr.s(slots=True, frozen=True)
class OfferScoreEncodingProgress:
    offer_acronym = attr.ib(type=str)
    progress_by_deadlines = attr.ib(type=List[DeadlineScoreEncodingProgress])

    @property
    def exam_enrollments_encoded(self) -> int:
        return sum(deadline_progress.exam_enrollments_encoded for deadline_progress in self.progress_by_deadlines)

    @property
    def scores_not_yet_submitted(self) -> int:
        return sum(deadline_progress.scores_not_yet_submitted for deadline_progress in self.progress_by_deadlines)

    @property
    def total_exam_enrollments(self) -> int:
        return sum(deadline_progress.total_exam_enrollments for deadline_progress in self.progress_by_deadlines)


@attr.s(slots=True, frozen=True)
class LearningUnitScoreEncodingProgress:
    learning_unit_year_acronym = attr.ib(type=str)
    learning_unit_year_full_title = attr.ib(type=str)
    offers_progress = attr.ib(type=List[OfferScoreEncodingProgress])
    tutors = attr.ib(type=List[Tutor])
    score_responsible = attr.ib(type=Tutor)
    # exam_enrollments_encoded = attr.ib(type=int)
    # scores_not_yet_submitted = attr.ib(type=int)
    # total_exam_enrollments = attr.ib(type=int)

    @property
    def progress_int(self) -> int:
        return (self.exam_enrollments_encoded / self.total_exam_enrollments) * 100

    @property
    def progress(self) -> str:
        return "{0:.0f}".format(self.progress_int)

    @property
    def exam_enrollments_encoded(self) -> int:
        return sum(offer_progress.exam_enrollments_encoded for offer_progress in self.offers_progress)

    @property
    def scores_not_yet_submitted(self) -> int:
        return sum(offer_progress.scores_not_yet_submitted for offer_progress in self.offers_progress)

    @property
    def total_exam_enrollments(self) -> int:
        return sum(offer_progress.total_exam_enrollments for offer_progress in self.offers_progress)

    @property
    def tutor_exam_deadlines(self) -> List[datetime.datetime]:
        return sorted(offer_progress.deadline_tutor for offer_progress in self.offers_progress)


def build_score_encoding_progress(user, offer_year_id, number_session, academic_year, learning_unit_year_ids=None):
    if offer_year_id:
        offer_year_ids = [offer_year_id]
    else:
        offer_year_ids = offer_year.find_by_user(user).values_list('id', flat=True)

    qs = LearningUnitYear.objects.filter(
        academic_year=academic_year,
        learningunitenrollment__examenrollment__session_exam__number_session=number_session,
        learnintunitenrollment__offer_enrollment__offer_year_id__in=offer_year_ids,
        enrollment_state=exam_enrollment_state.ENROLLED
    )

    if learning_unit_year_ids:
        qs = qs.filter(pk__in=learning_unit_year_ids)

    if not program_manager.is_program_manager(user):  # user is tutor
        qs = qs.filter(attribution__tutor__person__user=user)

    qs = qs.annotate(
        offers_progress=Subquery(
            OfferYear.objects.filter(
                pk__in=OuterRef('learningunitenrollment__offer_enrollment__offer_year_id')
            ).annotate(
                deadline_tutor=Subquery(
                    SessionExamDeadline.objects.filter(offer_enrollment__offer_year_i)
                )
            )
        )
    )

    exam_deadlines_qs = SessionExamDeadline.objects.filter(
        offer_enrollment__learningunitenrollment__learning_unit_year_id__in=qs.values_list('pk', flat=True)  # FIXME :: use list comprehension
    ).annotate(
        exam_enrollments_encoded=Subquery(
            ExamEnrollment.objects.filter(
                session_exam__number_session=number_session,
                learning_unit_enrollment__offer_enrollment__sessionexamdeadline__pk=OuterRef('pk')
            )
        ),
        # scores_not_yet_submitted
        # total_exam_enrollments
    ).distinct()


def get():
    return SessionExamDeadline.objects.filter(
        offer_enrollment__offer_year__academic_year__year=2019,
        number_session=3
    ).annotate(
        offer_acronym=F('offer_enrollment__offer_year__acronym')
    ).values(
        'offer_acronym', 'dead'
    ).annotate(
        exam_enrollments_encoded=Count(
            "offer_enrollment__learningunitenrollment__examenrollment",
            filter=Q(offer_enrollment__learningunitenrollment__examenrollment__session_exam__number_session=1)
        )
        # scores_not_yet_submitted
        # total_exam_enrollments
    )[:10]


# entity_requirement = entity_version.EntityVersion.objects.filter(
#     entity=OuterRef('learning_container_year__requirement_entity'),
# ).current(
#     OuterRef('academic_year__start_date')
# ).values('acronym')[:1]
# return queryset.annotate(
#     entity_requirement=Subquery(entity_requirement)
# )