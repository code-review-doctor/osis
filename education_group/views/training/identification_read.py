from django.http import Http404
from reversion.models import Version

from base.models.education_group_achievement import EducationGroupAchievement
from base.models.education_group_certificate_aim import EducationGroupCertificateAim
from base.models.education_group_detailed_achievement import EducationGroupDetailedAchievement
from base.models.education_group_organization import EducationGroupOrganization
from base.models.education_group_year_domain import EducationGroupYearDomain
from education_group.ddd.domain.exception import TrainingNotFoundException
from education_group.ddd.domain.training import TrainingIdentity
from education_group.ddd.repository.training import TrainingRepository
from education_group.models.group_year import GroupYear
from education_group.views.training.common_read import TrainingRead, Tab
from program_management.models.education_group_version import EducationGroupVersion


class TrainingReadIdentification(TrainingRead):
    template_name = "training/identification_read.html"
    active_tab = Tab.IDENTIFICATION

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "education_group_year": self.get_training(),  # TODO: Rename to training (DDD concept)
            "history": self.get_related_history(),
        }

    def get_related_history(self):
        education_group_year = self.education_group_version.offer
        versions = Version.objects.get_for_object(
            education_group_year
        ).select_related('revision__user__person')

        related_models = [
            EducationGroupOrganization,
            EducationGroupAchievement,
            EducationGroupDetailedAchievement,
            EducationGroupYearDomain,
            EducationGroupCertificateAim,
            EducationGroupVersion,
            GroupYear,
        ]

        subversion = Version.objects.none()
        for model in related_models:
            subversion |= Version.objects.get_for_model(model).select_related('revision__user__person')

        versions |= subversion.filter(
            serialized_data__contains="\"education_group_year\": {}".format(education_group_year.pk)
        )

        return versions.order_by('-revision__date_created').distinct('revision__date_created')

    def get_training(self):
        try:
            return TrainingRepository.get(
                TrainingIdentity(acronym=self.get_object().title, year=self.get_object().year)
            )
        except TrainingNotFoundException:
            raise Http404
