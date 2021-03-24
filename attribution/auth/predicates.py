from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rules import predicate

from attribution.models.attribution_new import AttributionNew
from base.models.learning_unit_year import LearningUnitYear
from osis_role.errors import predicate_failed_msg


@predicate(bind=True)
@predicate_failed_msg(message=_("You are not attributed to this learning unit."))
def have_attribution(self, user: User, obj: LearningUnitYear):
    if obj:
        return AttributionNew.objects.filter(
            tutor__person__user=user,
            learning_container_year=obj.learning_container_year
        ).exists()
    return None
