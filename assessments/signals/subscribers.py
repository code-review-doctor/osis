##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.dispatch import receiver
from base.business.scores_encodings_deadline import compute_deadline, compute_deadline_by_student, recompute_all_deadlines
from base.signals.publisher import compute_scores_encodings_deadlines, compute_student_score_encoding_deadline, compute_all_scores_encodings_deadlines


@receiver(compute_scores_encodings_deadlines)
def compute_scores_encodings_deadlines(sender, **kwargs):
    compute_deadline(kwargs['offer_year_calendar'])


@receiver(compute_student_score_encoding_deadline)
def compute_student_score_encoding_deadline(sender, **kwargs):
    compute_deadline_by_student(kwargs['session_exam_deadline'])


@receiver(compute_all_scores_encodings_deadlines)
def compute_all_scores_encodings_deadlines(sender, **kwargs):
    recompute_all_deadlines(kwargs['academic_calendar'])
