from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rules import predicate

from attribution.models.attribution_charge_new import AttributionChargeNew
from base.models.learning_unit_year import LearningUnitYear
from osis_role.errors import predicate_failed_msg


@predicate(bind=True)
@predicate_failed_msg(message=_("You are not attributed to this learning unit."))
def have_attribution_on_learning_unit_year(self, user: User, obj: LearningUnitYear):
    if obj:
        return AttributionChargeNew.objects.filter(
            attribution__tutor__person__user=user,
            learning_component_year__learning_unit_year=obj
        ).exists()
    return None
