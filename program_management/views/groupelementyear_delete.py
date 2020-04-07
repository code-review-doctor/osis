############################################################################
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
############################################################################
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView

from base.utils.cache import ElementCache
from base.views.common import display_error_messages, display_success_messages, display_warning_messages
from program_management.business.group_element_years.detach import DetachEducationGroupYearStrategy, \
    DetachLearningUnitYearStrategy
from program_management.views import perms as group_element_year_perms
from program_management.views.generic import GenericGroupElementYearMixin


class DetachGroupElementYearView(GenericGroupElementYearMixin, DeleteView):
    template_name = "group_element_year/confirm_detach_inner.html"

    rules = [group_element_year_perms.can_detach_group_element_year]

    def _call_rule(self, rule):
        return rule(self.request.user, self.get_object())

    @cached_property
    def strategy(self):
        obj = self.get_object()
        strategy_class = DetachEducationGroupYearStrategy if obj.child_branch else DetachLearningUnitYearStrategy
        return strategy_class(obj)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        msg = "%(acronym)s" % {"acronym": self.object.child.acronym}
        if hasattr(self.object.child, 'partial_acronym'):
            msg = "%(partial_acronym)s - %(acronym)s" % {
                "acronym": msg,
                "partial_acronym": self.object.child.partial_acronym
            }

        if self.strategy.is_valid():
            context['confirmation_message'] = _("Are you sure you want to detach %(acronym)s ?") % {
                "acronym": msg
            }
            display_warning_messages(self.request, self.strategy.warnings)
        else:
            display_error_messages(self.request, self.strategy.errors)
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self.strategy.is_valid():
            return JsonResponse({"error": True})
        self.strategy.post_valid()

        success_msg = _("\"%(child)s\" has been detached from \"%(parent)s\"") % {
            'child': obj.child,
            'parent': obj.parent,
        }

        self._remove_element_from_clipboard_if_stored(obj)

        display_success_messages(request, success_msg)
        return super().delete(request, *args, **kwargs)

    def _remove_element_from_clipboard_if_stored(self, obj_detached):
        element_cache = ElementCache(self.request.user)
        obj_detached = obj_detached.child_branch or obj_detached.child_leaf
        if element_cache.equals(obj_detached):
            element_cache.clear()

    def get_success_url(self):
        # We can just reload the page
        return

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                for rule in self.rules:
                    perm = rule(self.request.user, self.get_object())
                    if not perm:
                        break

            except PermissionDenied as e:

                return render(request,
                              'education_group/blocks/modal/modal_access_denied.html',
                              {'access_message': _('You are not eligible to detach this item')})

        return super(DetachGroupElementYearView, self).dispatch(request, *args, **kwargs)
