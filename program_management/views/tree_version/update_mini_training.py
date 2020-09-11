import functools
from typing import Dict, List

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import View
from django.utils.translation import gettext_lazy as _

from base.views.common import display_error_messages
from education_group.ddd.domain import exception as exception_education_group
from education_group.models.group_year import GroupYear
from education_group.templatetags.academic_year_display import display_as_academic_year
from osis_role.contrib.views import PermissionRequiredMixin

from education_group.ddd.business_types import *
from education_group.ddd import command as command_education_group
from education_group.ddd.domain.exception import GroupNotFoundException, \
    MiniTrainingNotFoundException
from education_group.ddd.service.read import get_group_service, get_mini_training_service

from program_management.ddd.business_types import *
from program_management.ddd import command
from program_management.ddd.command import UpdateMiniTrainingVersionCommand
from program_management.ddd.service.read import get_program_tree_version_from_node_service
from program_management.ddd.service.write import update_mini_training_version_service
from program_management.forms import version


class MiniTrainingVersionUpdateView(PermissionRequiredMixin, View):
    permission_required = 'base.change_educationgroup'
    raise_exception = True

    template_name = "tree_version/mini_training/update.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_program_tree_version_obj().is_standard_version:
            redirect_url = reverse('mini_training_update', kwargs={
                'year': self.get_group_obj().year,
                'code':  self.get_group_obj().code,
                'acronym': self.get_mini_training_obj().acronym
            })
            return HttpResponseRedirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {
            "mini_training_version_form": self.mini_training_version_form,
            "mini_training_obj": self.get_mini_training_obj(),
            "mini_training_version_obj": self.get_program_tree_version_obj(),
            "group_obj": self.get_group_obj(),
            "tabs": self.get_tabs(),
            "cancel_url": self.get_cancel_url()
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if self.mini_training_version_form.is_valid():
            self.update_mini_training_version()
            if not self.mini_training_version_form.errors:
                return HttpResponseRedirect(self.get_success_url())
        display_error_messages(self.request, self._get_default_error_messages())
        return self.get(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse(
            'element_identification',
            kwargs={'code': self.kwargs['code'], 'year': self.kwargs['year']},
        )

    def get_cancel_url(self) -> str:
        return self.get_success_url()

    def update_mini_training_version(self):
        try:
            update_command = self._convert_form_to_update_mini_training_version_command(self.mini_training_version_form)
            return update_mini_training_version_service.update_mini_training_version(update_command)
        except exception_education_group.ContentConstraintTypeMissing as e:
            self.mini_training_version_form.add_error("constraint_type", e.message)
        except (exception_education_group.ContentConstraintMinimumMaximumMissing,
                exception_education_group.ContentConstraintMaximumShouldBeGreaterOrEqualsThanMinimum) as e:
            self.mini_training_version_form.add_error("min_constraint", e.message)
            self.mini_training_version_form.add_error("max_constraint", "")
        return []

    @cached_property
    def mini_training_version_form(self) -> 'version.UpdateMiniTrainingVersionForm':
        mini_training_version_identity = self.get_program_tree_version_obj().entity_id
        node_identity = self.get_program_tree_obj().root_node.entity_id
        return version.UpdateMiniTrainingVersionForm(
            data=self.request.POST or None,
            user=self.request.user,
            mini_training_version_identity=mini_training_version_identity,
            node_identity=node_identity,
            initial=self._get_mini_training_version_form_initial_values(),
            mini_training_type=self.get_mini_training_obj().type
        )

    @functools.lru_cache()
    def get_mini_training_obj(self) -> 'MiniTraining':
        try:
            mini_training_abbreviated_title = self.get_program_tree_version_obj().entity_id.offer_acronym
            get_cmd = command_education_group.GetMiniTrainingCommand(
                acronym=mini_training_abbreviated_title,
                year=self.kwargs['year']
            )
            return get_mini_training_service.get_mini_training(get_cmd)
        except MiniTrainingNotFoundException:
            raise Http404

    @functools.lru_cache()
    def get_group_obj(self) -> 'Group':
        try:
            get_cmd = command_education_group.GetGroupCommand(
                code=self.kwargs["code"],
                year=self.kwargs["year"]
            )
            return get_group_service.get_group(get_cmd)
        except GroupNotFoundException:
            raise Http404

    @functools.lru_cache()
    def get_program_tree_version_obj(self) -> 'ProgramTreeVersion':
        get_cmd = command.GetProgramTreeVersionFromNodeCommand(
            code=self.kwargs['code'],
            year=self.kwargs['year']
        )
        return get_program_tree_version_from_node_service.get_program_tree_version_from_node(get_cmd)

    @functools.lru_cache()
    def get_program_tree_obj(self) -> 'ProgramTree':
        return self.get_program_tree_version_obj().get_tree()

    def get_permission_object(self):
        return GroupYear.objects.select_related('management_entity').get(
            partial_acronym=self.kwargs['code'],
            academic_year__year=self.kwargs['year']
        )

    def get_tabs(self) -> List:
        return [
            {
                "text": _("Identification"),
                "active": True,
                "display": True,
                "include_html": "tree_version/mini_training/blocks/identification.html"
            },
        ]

    def _get_default_error_messages(self) -> str:
        return _("Error(s) in form: The modifications are not saved")

    def _get_mini_training_version_form_initial_values(self) -> Dict:
        mini_training_version = self.get_program_tree_version_obj()
        mini_training_obj = self.get_mini_training_obj()
        group_obj = self.get_group_obj()

        form_initial_values = {
            'version_name': mini_training_version.version_name,
            'version_title_fr': mini_training_version.title_fr,
            'version_title_en': mini_training_version.title_en,
            'end_year': mini_training_version.end_year_of_existence,

            "category": _("Mini-Training"),
            "type": mini_training_obj.type.value,
            "offer_title_fr": mini_training_obj.titles.title_fr,
            "offer_title_en": mini_training_obj.titles.title_en,
            "academic_year": mini_training_obj.academic_year,
            "code": group_obj.code,
            "status": mini_training_obj.status.value,
            "schedule_type": mini_training_obj.schedule_type.value,
            "credits": group_obj.credits,
            "constraint_type": group_obj.content_constraint.type.value
            if group_obj.content_constraint.type else None,
            "min_constraint": group_obj.content_constraint.minimum,
            "max_constraint": group_obj.content_constraint.maximum,
            "keywords": mini_training_obj.keywords,
            "remark_fr": group_obj.remark.text_fr,
            "remark_en": group_obj.remark.text_en,
            "management_entity": group_obj.management_entity.acronym,
            "start_year": display_as_academic_year(mini_training_obj.start_year),
            "teaching_campus": group_obj.teaching_campus.name,
        }
        return form_initial_values

    def _convert_form_to_update_mini_training_version_command(
            self, form: 'version.UpdateMiniTrainingVersionForm'
    ) -> UpdateMiniTrainingVersionCommand:
        return UpdateMiniTrainingVersionCommand(
            offer_acronym=self.get_program_tree_version_obj().entity_id.offer_acronym,
            version_name=self.get_program_tree_version_obj().entity_id.version_name,
            year=self.get_program_tree_version_obj().entity_id.year,
            is_transition=self.get_program_tree_version_obj().entity_id.is_transition,

            title_en=form.cleaned_data["version_title_en"],
            title_fr=form.cleaned_data["version_title_fr"],
            end_year=form.cleaned_data["end_year"],
            management_entity_acronym=form.cleaned_data['management_entity'],
            teaching_campus_name=form.cleaned_data['teaching_campus'].name if form.cleaned_data["teaching_campus"]
            else None,
            teaching_campus_organization_name=form.cleaned_data['teaching_campus'].organization.name
            if form.cleaned_data["teaching_campus"] else None,
            credits=form.cleaned_data['credits'],
            constraint_type=form.cleaned_data['constraint_type'],
            min_constraint=form.cleaned_data['min_constraint'],
            max_constraint=form.cleaned_data['max_constraint'],
            remark_fr=form.cleaned_data['remark_fr'],
            remark_en=form.cleaned_data['remark_en'],
        )
