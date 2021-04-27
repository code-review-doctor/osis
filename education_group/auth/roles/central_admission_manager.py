import rules
from django.utils.translation import gettext_lazy as _

from education_group.auth import predicates
from osis_role.contrib import models as osis_role_models


class CentralAdmissionManager(osis_role_models.RoleModel):
    """
        Previously called SIC
    """
    class Meta:
        verbose_name = _("Central admission manager")
        verbose_name_plural = _("Central admission manager")
        group_name = "central_admission_managers"

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
            'base.view_educationgroup': rules.always_allow,
            'base.can_access_catalog_configuration': rules.always_allow,
            'base.change_commonadmissioncondition':
                predicates.is_education_group_extended_daily_management_calendar_open,
            'base.can_access_catalog': rules.always_allow,  # Perms Backward compibility
        })
