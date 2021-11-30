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
import rules
from django.db import models
from django.utils.translation import gettext_lazy as _

from osis_role.contrib.admin import RoleModelAdmin
from osis_role.contrib.models import RoleModel


class CatalogViewerAdmin(RoleModelAdmin):
    list_display = ('person', 'changed')
    list_filter = ('person__gender', 'person__language')
    search_fields = ['person__first_name', 'person__last_name', 'person__global_id']


class CatalogViewer(RoleModel):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    person = models.OneToOneField('Person', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Catalog viewer")
        verbose_name_plural = _("Catalog viewers")
        group_name = "catalog_viewers"

    def __str__(self):
        return u"%s" % self.person

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
            'base.can_access_learningunitcomponentyear': rules.always_allow,
            'base.can_access_learningcontaineryear': rules.always_allow,
            'base.can_access_learningunit': rules.always_allow,
            'base.can_access_externallearningunityear': rules.always_allow,
            'base.view_educationgroup': rules.always_allow,
            'base.can_access_catalog': rules.always_allow,
            'learning_unit.view_learningclassyear': rules.always_allow
        })
