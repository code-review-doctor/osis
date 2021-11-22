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
import itertools
from typing import Iterable, List, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from reversion.models import Version

from attribution.models.attribution_new import AttributionNew
from base.business.learning_unit import get_achievements_group_by_language, CMS_LABEL_PEDAGOGY_FR_ONLY
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import get_user_interface_language, Person
from base.models.teaching_material import TeachingMaterial
from base.views.learning_unit import get_specifications_context, get_languages_settings
from base.views.learning_units.common import get_common_context_for_learning_unit_year
from base.views.learning_units.pedagogy.read import _get_cms_pedagogy_labels_translated, \
    _get_cms_force_majeure_labels_translated, _get_modification_history
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from learning_unit.calendar.learning_unit_force_majeur_summary_edition import \
    LearningUnitForceMajeurSummaryEditionCalendar
from learning_unit.calendar.learning_unit_summary_edition_calendar import LearningUnitSummaryEditionCalendar
from osis_role.contrib.views import PermissionRequiredMixin


class EducationalInformation(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'base.can_access_learningunit_pedagogy'
    template_name = 'manage_my_courses/educational_information.html'

    @cached_property
    def learning_unit_year(self) -> LearningUnitYear:
        return get_object_or_404(
            LearningUnitYear.objects.all().select_related(
                'learning_unit', 'learning_container_year', 'academic_year'
            ),
            pk=self.kwargs['learning_unit_year_id']
        )

    def get_permission_object(self) -> LearningUnitYear:
        return self.learning_unit_year

    @cached_property
    def person(self) -> Person:
        return get_object_or_404(Person, user=self.request.user)

    @cached_property
    def user_language(self) -> str:
        return get_user_interface_language(self.request.user)

    @cached_property
    def teaching_materials(self) -> List[TeachingMaterial]:
        return TeachingMaterial.objects.filter(learning_unit_year=self.learning_unit_year).order_by('order')

    @cached_property
    def attributions(self) -> List[AttributionNew]:
        return AttributionNew.objects.filter(
            attributionchargenew__learning_component_year__learning_unit_year=self.learning_unit_year
        ).select_related(
            "tutor__person"
        ).distinct().order_by("tutor__person")

    @cached_property
    def pedagogy_translated_labels(self) -> List[TranslatedTextLabel]:
        return _get_cms_pedagogy_labels_translated(
            self.kwargs['learning_unit_year_id'],
            self.user_language
        )

    @cached_property
    def force_majeure_translated_labels(self) -> List[TranslatedTextLabel]:
        return _get_cms_force_majeure_labels_translated(
            self.kwargs['learning_unit_year_id'],
            self.user_language
        )

    @cached_property
    def pedagogy_history(self) -> Version:
        translated_text_ids = itertools.chain.from_iterable(
            (*translated_label.text_label.text_fr, *translated_label.text_label.text_en)
            for translated_label in list(self.pedagogy_translated_labels)
        )
        cms_pedagogy_last_modification_qs = Q(
            content_type=ContentType.objects.get_for_model(TranslatedText),
            object_id__in=map(lambda obj: obj.id, translated_text_ids)
        ) | Q(
            content_type=ContentType.objects.get_for_model(TeachingMaterial),
            object_id__in=map(lambda obj: obj.id, self.teaching_materials)
        )
        return _get_modification_history(cms_pedagogy_last_modification_qs)

    @cached_property
    def force_majeure_history(self) -> Version:
        force_majeure_translated_text_ids = itertools.chain.from_iterable(
            (*translated_label.text_label.text_fr, *translated_label.text_label.text_en)
            for translated_label in list(self.force_majeure_translated_labels)
        )
        cms_force_majeure_last_modification_qs = Q(
            content_type=ContentType.objects.get_for_model(TranslatedText),
            object_id__in=map(lambda obj: obj.id, force_majeure_translated_text_ids)
        )
        return _get_modification_history(cms_force_majeure_last_modification_qs)

    @staticmethod
    def get_context_actions_url() -> Dict[str, str]:
        return {
            'create_teaching_material_urlname': 'tutor_teaching_material_create',
            'update_teaching_material_urlname': 'tutor_teaching_material_edit',
            'delete_teaching_material_urlname': 'tutor_teaching_material_delete',
            'update_mobility_modality_urlname': 'tutor_mobility_modality_update',
        }

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **get_languages_settings(),
            **get_specifications_context(self.learning_unit_year, self.request),
            **get_common_context_for_learning_unit_year(self.person, self.learning_unit_year),
            **self.get_context_actions_url(),
            'submission_dates': LearningUnitSummaryEditionCalendar().get_academic_event(
                self.learning_unit_year.academic_year.year
            ),
            'force_majeure_submission_dates': LearningUnitForceMajeurSummaryEditionCalendar().get_academic_event(
                self.learning_unit_year.academic_year.year
            ),
            'achievements': _fetch_achievements_by_language(self.learning_unit_year),
            'div_class': 'collapse',
            'cms_labels_translated': self.pedagogy_translated_labels,
            'cms_force_majeure_labels_translated': _get_cms_force_majeure_labels_translated(
                self.kwargs['learning_unit_year_id'],
                self.user_language
            ),
            'teaching_materials': self.teaching_materials,
            'can_edit_summary_locked_field': self.person.user.has_perm(
                'base.can_edit_summary_locked_field', self.learning_unit_year
            ),
            'cms_label_pedagogy_fr_only': CMS_LABEL_PEDAGOGY_FR_ONLY,
            'attributions': self.attributions,
            "version": self.pedagogy_history,
            "force_majeure_version": self.force_majeure_history,
        }


def _fetch_achievements_by_language(learning_unit_year: LearningUnitYear) -> Iterable:
    fr_achievement_code = "achievements_FR"
    en_achievement_code = "achievements_EN"
    achievements = get_achievements_group_by_language(learning_unit_year)
    return itertools.zip_longest(achievements.get(fr_achievement_code, []), achievements.get(en_achievement_code, []))
