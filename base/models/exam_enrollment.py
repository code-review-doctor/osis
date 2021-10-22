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

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext as _

from base.models import person
from base.models.enums import exam_enrollment_justification_type as justification_types
from base.models.enums import exam_enrollment_state as enrollment_states
from base.models.enums import number_session
from base.models.exceptions import JustificationValueException
from base.models.utils.admin_extentions import remove_delete_action
from osis_common.models.osis_model_admin import OsisModelAdmin

SCORE_BETWEEN_0_AND_20 = _("Scores must be between 0 and 20")


class ExamEnrollmentAdmin(OsisModelAdmin):
    list_display = (
        'learning_unit_enrollment',
        'enrollment_state',
        'session_exam',
        'score_draft',
        'justification_draft',
        'score_final',
        'justification_final',
        'score_reencoded',
        'justification_reencoded',
        'changed',
    )
    list_filter = ('session_exam__number_session', 'learning_unit_enrollment__learning_unit_year__academic_year')
    search_fields = ['learning_unit_enrollment__offer_enrollment__student__person__first_name',
                     'learning_unit_enrollment__offer_enrollment__student__person__last_name',
                     'learning_unit_enrollment__offer_enrollment__student__registration_id',
                     'learning_unit_enrollment__learning_unit_year__acronym',
                     'learning_unit_enrollment__offer_enrollment__education_group_year__acronym']


class ExamEnrollment(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    score_draft = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True,
                                      validators=[MinValueValidator(0, message=SCORE_BETWEEN_0_AND_20),
                                                  MaxValueValidator(20, message=SCORE_BETWEEN_0_AND_20)])
    score_reencoded = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True,
                                          validators=[MinValueValidator(0,
                                                                        message=SCORE_BETWEEN_0_AND_20),
                                                      MaxValueValidator(20,
                                                                        message=SCORE_BETWEEN_0_AND_20)])
    score_final = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True,
                                      validators=[MinValueValidator(0, message=SCORE_BETWEEN_0_AND_20),
                                                  MaxValueValidator(20, message=SCORE_BETWEEN_0_AND_20)])
    justification_draft = models.CharField(max_length=20, blank=True, null=True,
                                           choices=justification_types.JUSTIFICATION_TYPES)
    justification_reencoded = models.CharField(max_length=20, blank=True, null=True,
                                               choices=justification_types.JUSTIFICATION_TYPES)
    justification_final = models.CharField(max_length=20, blank=True, null=True,
                                           choices=justification_types.JUSTIFICATION_TYPES)
    session_exam = models.ForeignKey('SessionExam', on_delete=models.CASCADE)
    learning_unit_enrollment = models.ForeignKey('LearningUnitEnrollment', on_delete=models.PROTECT)
    enrollment_state = models.CharField(max_length=20,
                                        default=enrollment_states.ENROLLED,
                                        choices=enrollment_states.STATES,
                                        db_index=True)
    date_enrollment = models.DateField(null=True, blank=True, verbose_name=_("Enrollment date"))

    def student(self):
        return self.learning_unit_enrollment.student

    def justification_valid(self):
        valid_justifs = [j[0] for j in justification_types.JUSTIFICATION_TYPES]
        if self.justification_draft:
            if self.justification_draft not in valid_justifs:
                return False
        if self.justification_reencoded:
            if self.justification_reencoded not in valid_justifs:
                return False
        if self.justification_final:
            if self.justification_final not in valid_justifs:
                return False
        return True

    def save(self, *args, **kwargs):
        if not self.justification_valid():
            raise JustificationValueException
        super(ExamEnrollment, self).save(*args, **kwargs)

    def __str__(self):
        return u"%s - %s" % (self.session_exam, self.learning_unit_enrollment)


def justification_label_authorized():
    return "%s, %s" % (_('A=Absent'),
                       _('T=Cheating'))


class ExamEnrollmentHistoryAdmin(OsisModelAdmin):
    list_display = ('person', 'score_final', 'justification_final', 'modification_date', 'exam_enrollment')
    raw_id_fields = ('exam_enrollment', 'person')
    search_fields = ['exam_enrollment__learning_unit_enrollment__offer_enrollment__student__person__first_name',
                     'exam_enrollment__learning_unit_enrollment__offer_enrollment__student__person__last_name',
                     'exam_enrollment__learning_unit_enrollment__offer_enrollment__student__registration_id',
                     'exam_enrollment__learning_unit_enrollment__learning_unit_year__acronym']
    list_filter = ('exam_enrollment__learning_unit_enrollment__learning_unit_year__academic_year',)
    readonly_fields = ('exam_enrollment', 'person', 'score_final', 'justification_final', 'modification_date')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        return remove_delete_action(super(ExamEnrollmentHistoryAdmin, self).get_actions(request))


class ExamEnrollmentHistory(models.Model):
    exam_enrollment = models.ForeignKey(ExamEnrollment, on_delete=models.CASCADE)
    person = models.ForeignKey(person.Person, on_delete=models.PROTECT)
    score_final = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    justification_final = models.CharField(max_length=20, null=True, choices=justification_types.JUSTIFICATION_TYPES)
    modification_date = models.DateTimeField(auto_now=True)


def create_exam_enrollment_historic(user, enrollment):
    exam_enrollment_history = ExamEnrollmentHistory()
    exam_enrollment_history.exam_enrollment = enrollment
    exam_enrollment_history.score_final = enrollment.score_final
    exam_enrollment_history.justification_final = enrollment.justification_final
    exam_enrollment_history.person = person.find_by_user(user)
    exam_enrollment_history.save()
