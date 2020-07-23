##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
import re

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import FormView

from base.business.education_groups import perms
from base.forms.education_group.common import EducationGroupModelForm
from base.forms.education_group.group import GroupForm
from base.forms.education_group.mini_training import MiniTrainingForm
from base.forms.education_group.training import TrainingForm
from base.forms.education_group.version import SpecificVersionForm
from base.models.academic_year import starting_academic_year, AcademicYear
from base.models.education_group_type import EducationGroupType
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from base.models.enums.education_group_types import TrainingType
from base.models.exceptions import ValidationWarning
from base.utils.cache import RequestCache
from base.views.common import display_success_messages, show_error_message_for_form_invalid
from base.views.mixins import AjaxTemplateMixin
from osis_common.decorators.ajax import ajax_required
from osis_common.utils.models import get_object_or_none
from osis_role import errors
from osis_role.contrib.views import AjaxPermissionRequiredMixin
from program_management.models.education_group_version import EducationGroupVersion

FORMS_BY_CATEGORY = {
    education_group_categories.GROUP: GroupForm,
    education_group_categories.TRAINING: TrainingForm,
    education_group_categories.MINI_TRAINING: MiniTrainingForm,
}

TEMPLATES_BY_CATEGORY = {
    education_group_categories.GROUP: "education_group/create_groups.html",
    education_group_categories.TRAINING: "education_group/create_trainings.html",
    education_group_categories.MINI_TRAINING: "education_group/create_mini_trainings.html",
}

PERMS_BY_CATEGORY = {
    education_group_categories.GROUP: 'base.add_group',
    education_group_categories.TRAINING: 'base.add_training',
    education_group_categories.MINI_TRAINING: 'base.add_minitraining',
}


# TODO: Split create into create_groups/create_training/create_minitraining
#  in order to user decorator permission_required
@login_required
def create_education_group(request, category, education_group_type_pk, root_id=None, parent_id=None):
    parent = get_object_or_none(EducationGroupYear, pk=parent_id)
    education_group_type = get_object_or_404(EducationGroupType, pk=education_group_type_pk)

    perm = PERMS_BY_CATEGORY[category]
    if not request.user.has_perm(perm, parent):
        raise PermissionDenied(errors.get_permission_error(request.user, perm))

    request_cache = RequestCache(request.user, reverse('version_program'))
    cached_data = request_cache.cached_data or {}
    academic_year = cached_data.get('academic_year')
    if not academic_year:
        cached_data['academic_year'] = starting_academic_year()

    initial_academic_year = parent.academic_year_id if parent else cached_data.get('academic_year')
    form_education_group_year = FORMS_BY_CATEGORY[category](
        request.POST or None,
        parent=parent,
        user=request.user,
        education_group_type=education_group_type,
        initial={'academic_year': initial_academic_year}
    )

    if request.method == 'POST':
        if form_education_group_year.is_valid():
            return _common_success_redirect(request, form_education_group_year, root_id)
        else:
            show_error_message_for_form_invalid(request)

    data = {
        "form_education_group_year": form_education_group_year.forms[forms.ModelForm],
        "form_education_group": form_education_group_year.forms[EducationGroupModelForm],
        "parent": parent,
        'root_pk': root_id,
        "is_finality_types": education_group_type.name in TrainingType.finality_types()
    }

    if category == education_group_categories.TRAINING:
        data.update(
            {
                "form_hops": form_education_group_year.hops_form,
                "show_diploma_tab": form_education_group_year.show_diploma_tab(),
            }
        )

    return render(request, TEMPLATES_BY_CATEGORY.get(category), data)


def _common_success_redirect(request, form, root_id=None):
    education_group_year = form.save()
    if not root_id:
        root_id = education_group_year.pk
    success_msg = [_get_success_message_for_creation_education_group_year(root_id, education_group_year)]
    if hasattr(form, 'education_group_year_postponed'):
        success_msg += [
            _get_success_message_for_creation_education_group_year(egy.id, egy)
            for egy in form.education_group_year_postponed
        ]
    display_success_messages(request, success_msg, extra_tags='safe')

    # Redirect
    url = reverse(
        "element_identification",
        kwargs={
            "year": education_group_year.academic_year.year,
            "code": education_group_year.partial_acronym
        }
    )
    return redirect(url)


def _get_success_message_for_creation_education_group_year(root_id, education_group_year):
    link = reverse("element_identification", kwargs={
            "year": education_group_year.academic_year.year,
            "code": education_group_year.partial_acronym
        }
    )
    return _("Education group year <a href='%(link)s'> %(acronym)s (%(academic_year)s) </a> successfully created.") % {
        "link": link,
        "acronym": education_group_year.acronym,
        "academic_year": education_group_year.academic_year,
    }


@ajax_required
@login_required
def validate_field(request, category, education_group_year_pk=None):
    accepted_fields = ["partial_acronym", "acronym"]

    academic_year = AcademicYear.objects.get(pk=request.GET["academic_year"])
    acronym = request.GET.get("acronym")
    partial_acronym = request.GET.get("partial_acronym")

    egy = EducationGroupYear(academic_year=academic_year, acronym=acronym, partial_acronym=partial_acronym,
                             education_group_type=EducationGroupType(category=category))

    # This is an update
    if education_group_year_pk:
        egy = get_object_or_404(EducationGroupYear, pk=education_group_year_pk)
        egy.acronym = acronym
        egy.partial_acronym = partial_acronym

    response = {}

    for field in accepted_fields:
        try:
            attr_name = 'clean_{field_name}'.format(field_name=field)
            clean_field_func = getattr(egy, attr_name)
            if clean_field_func:
                clean_field_func(raise_warnings=True)
        except ValidationWarning as w:
            response[field] = {'msg': w.message_dict[field][0], 'level': messages.DEFAULT_TAGS[messages.WARNING]}
        except ValidationError as e:
            response[field] = {'msg': e.message_dict[field][0], 'level': messages.DEFAULT_TAGS[messages.ERROR]}

    return JsonResponse(response)


class CreateProgramTreeVersion(AjaxPermissionRequiredMixin, SuccessMessageMixin, AjaxTemplateMixin, CreateView):
    template_name = "education_group/create_specific_version_inner.html"
    form_class = SpecificVersionForm
    permission_required = 'base.create_specific_version'

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def education_group_year(self):
        return get_object_or_404(
            EducationGroupYear,
            academic_year__year=self.kwargs['year'],
            acronym=self.kwargs['code'],
        )

    def _call_rule(self, rule):
        return rule(self.person, self.education_group_year)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["save_type"] = self.request.POST.get("save_type")
        form_kwargs['education_group_year'] = self.education_group_year
        form_kwargs['person'] = self.person
        form_kwargs.pop('instance')
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateProgramTreeVersion, self).get_context_data(**kwargs)
        context['education_group_year'] = self.education_group_year
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def get_success_message(self, cleaned_data):
        display_success_messages(self.request, cleaned_data["messages"])

    def get_success_url(self):
        return reverse(
            "training_identification",
            args=[
                self.education_group_year.academic_year.year,
                self.education_group_year.partial_acronym,
            ]
        )


@login_required
@ajax_required
def check_version_name(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    version_name = education_group_year.acronym + request.GET['version_name']
    existed_version_name = False
    existing_version_name = check_existing_version(version_name, education_group_year_id)
    last_using = None
    old_specific_versions = find_last_existed_version(education_group_year, version_name)
    if old_specific_versions:
        last_using = str(old_specific_versions.offer.academic_year)
        existed_version_name = True
    valid = bool(re.match("^[A-Z]{0,15}$", request.GET['version_name'].upper()))
    return JsonResponse({
        "existed_version_name": existed_version_name,
        "existing_version_name": existing_version_name,
        "last_using": last_using,
        "valid": valid,
        "version_name": request.GET['version_name']}, safe=False)


def check_existing_version(version_name: str, education_group_year_id: int) -> bool:
    return EducationGroupVersion.objects.filter(
        version_name=version_name,
        offer__id=education_group_year_id,
    ).exists()


def find_last_existed_version(education_group_year, version_name):
    return EducationGroupVersion.objects.filter(
        version_name=version_name,
        offer__education_group=education_group_year.education_group,
        offer__academic_year__year__lt=education_group_year.academic_year.year,
    ).order_by(
        'offer__academic_year'
    ).last()
