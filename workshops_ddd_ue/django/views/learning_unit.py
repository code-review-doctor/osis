from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import View

from base.views.common import display_success_messages
from workshops_ddd_ue.domain.learning_unit_year import LearningUnitIdentity
from workshops_ddd_ue.django.forms.learning_unit import LearningUnitCreateForm


class LearningUnitCreateView(View):

    template_name = "workshop/learning_unit_create.html"

    def get(self, request, *args, **kwargs):
        form = LearningUnitCreateForm(
            user=self.request.user,
        )
        return render(request, self.template_name, {
            "form": form,
        })

    def post(self, request, *args, **kwargs):
        form = LearningUnitCreateForm(request.POST, user=self.request.user)
        if form.is_valid():
            learning_unit_identity = form.save()
            if not form.errors:
                display_success_messages(request, self.get_success_msg(learning_unit_identity), extra_tags='safe')

        return render(request, self.template_name, {
            "form": form,
        })

    def get_success_msg(self, learning_unit_identity: LearningUnitIdentity):
        return _("Learning unit %(code)s (%(academic_year)s) successfully created.") % {
            "code": learning_unit_identity.code,
            "academic_year": learning_unit_identity.academic_year,
        }
