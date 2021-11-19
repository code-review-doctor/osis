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
import requests
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import DetailView
from django_filters.views import FilterView
from requests.exceptions import RequestException

from backoffice.settings.base import ESB_STUDENT_API, ESB_AUTHORIZATION
from base.api.serializers.student import StudentListSerializer
from base.forms.student import StudentFilter
from base.models.exam_enrollment import ExamEnrollment
from base.models.learning_unit_enrollment import LearningUnitEnrollment
from base.models.offer_enrollment import OfferEnrollment
from base.models.student import Student
from base.utils.cache import CacheFilterMixin
from base.utils.search import SearchMixin


class StudentSearch(PermissionRequiredMixin, SearchMixin, CacheFilterMixin, FilterView):
    model = Student
    paginate_by = 25
    template_name = "student/students.html"
    raise_exception = True

    filterset_class = StudentFilter
    permission_required = 'base.can_access_student'

    def get_filterset_kwargs(self, filterset_class):
        return {
            **super().get_filterset_kwargs(filterset_class),
        }

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            serializer = StudentListSerializer(context['object_list'], many=True)
            return JsonResponse({'object_list': serializer.data})
        return super().render_to_response(context, **response_kwargs)


class StudentRead(PermissionRequiredMixin, DetailView):
    permission_required = 'base.can_access_learningunit'
    raise_exception = True

    template_name = "student/student.html"

    pk_url_kwarg = "student_id"
    context_object_name = "student"

    model = Student

    def get(self, request, *args, **kwargs):
        student_id = kwargs['student_id']
        student = get_object_or_404(Student, pk=student_id)
        context = {'student': student}
        offer_enrollments = OfferEnrollment.objects.filter(
            student=student_id
        ).select_related(
            "education_group_year",
            "education_group_year__academic_year"
        ).order_by(
            '-education_group_year__academic_year__year',
            'education_group_year__acronym'
        )

        learning_unit_enrollments = LearningUnitEnrollment.objects.filter(
            offer_enrollment__student=student_id
        ).select_related(
            "learning_unit_year",
            "learning_unit_year__academic_year"
        ).order_by(
            '-learning_unit_year__academic_year__year',
            'learning_unit_year__acronym'
        )

        exam_enrollments = ExamEnrollment.objects.filter(
            learning_unit_enrollment__offer_enrollment__student=student_id
        ).select_related(
            "session_exam",
            "learning_unit_enrollment__learning_unit_year",
            "learning_unit_enrollment__learning_unit_year__academic_year"
        ).order_by(
            '-learning_unit_enrollment__learning_unit_year__academic_year__year',
            'session_exam__number_session',
            'learning_unit_enrollment__learning_unit_year__acronym'
        )
        context.update(
            {
                "student": student,
                "offer_enrollments": offer_enrollments,
                "learning_unit_enrollments": learning_unit_enrollments,
                "exam_enrollments": exam_enrollments
            }
        )
        return render(request, self.template_name, context)


@login_required
@permission_required('base.can_access_student', raise_exception=True)
def student_picture(request, student_id):
    student = get_object_or_404(Student.objects.select_related("person"), id=student_id)
    try:
        url = "{url}/{registration_id}/photo".format(url=ESB_STUDENT_API, registration_id=student.registration_id)
        response = requests.get(url, headers={"Authorization": ESB_AUTHORIZATION})
        result = response.json()
        if response.status_code == 200 and result.get('photo_url'):
            return _get_image(result.get('photo_url'), student)
    except (RequestException, ValueError):
        return _default_image(student)


def _get_image(url, student):
    response = requests.get(url)
    if response.status_code == 200:
        return HttpResponse(response.content, content_type="image/jpeg")
    return _default_image(student)


def _default_image(student):
    if student.person and student.person.gender == 'F':
        default_image = 'women_unknown'
    else:
        default_image = 'men_unknown'

    path = 'img/{}.png'.format(default_image)
    return redirect(staticfiles_storage.url(path))
