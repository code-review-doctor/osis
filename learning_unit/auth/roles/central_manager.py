import rules
from django.utils.translation import gettext_lazy as _

from learning_unit.auth import predicates
from osis_role.contrib import admin as osis_role_admin
from osis_role.contrib import models as osis_role_models


class CentralManagerAdmin(osis_role_admin.EntityRoleModelAdmin):
    list_display = osis_role_admin.EntityRoleModelAdmin.list_display


class CentralManager(osis_role_models.EntityRoleModel):
    class Meta:
        default_related_name = 'learning_unit'
        verbose_name = _("Central manager")
        verbose_name_plural = _("Central managers")
        group_name = "central_managers_for_ue"

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
            'base.can_create_learningunit': rules.always_allow,
            'base.can_create_partim':
                predicates.is_user_attached_to_current_management_entity &
                predicates.is_learning_unit_year_not_in_past &
                predicates.is_edition_period_open &
                predicates.is_learning_unit_year_full &
                predicates.is_external_learning_unit_cograduation,
            'base.can_access_learningunit': rules.always_allow,
            'base.can_delete_learningunit':
                predicates.is_learning_unit_container_type_deletable &
                predicates.is_user_attached_to_current_management_entity &
                predicates.is_learning_unit_year_prerequisite &
                predicates.has_learning_unit_applications,
            'base.can_edit_learningunit':
                predicates.is_user_attached_to_current_management_entity &
                predicates.is_learning_unit_year_older_or_equals_than_limit_settings_year &
                predicates.is_edition_period_open &
                predicates.is_external_learning_unit_cograduation &
                predicates.is_not_proposal,
            'base.add_externallearningunityear': rules.always_allow,
            'base.can_propose_learningunit':
                predicates.is_learning_unit_year_not_in_past &
                predicates.is_learning_unit_year_not_a_partim &
                predicates.is_learning_unit_container_type_editable &
                predicates.is_not_proposal &
                predicates.is_user_attached_to_current_management_entity &
                predicates.is_external_learning_unit_cograduation,
            'base.can_cancel_proposal':
                predicates.is_not_proposal_of_type_creation_with_applications &
                predicates.is_user_attached_to_current_management_entity |
                predicates.is_user_attached_to_initial_management_entity &
                predicates.is_external_learning_unit_cograduation,
            'base.can_edit_learningunit_date':
                predicates.is_learning_unit_year_older_or_equals_than_limit_settings_year &
                predicates.is_learning_unit_year_not_in_past
            ,
            'base.can_edit_learningunit_pedagogy': rules.always_allow,
            'base.can_edit_learningunit_specification': rules.always_allow,
            'base.can_consolidate_learningunit_proposal': rules.always_allow,
        })
