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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from backoffice.celery import app as celery_app
from base.business.education_groups.access_requirements import bulk_postpone_access_requirements, \
    bulk_postpone_access_requirements_line
from base.business.education_groups.achievement import bulk_postpone_achievements
from base.business.education_groups.publication_contact import bulk_postpone_publication_contact, \
    bulk_postpone_publication_entity
from base.models.education_group_year import EducationGroupYear

from education_group.ddd.command import PostponeGroupsUntilNPlus6Command, PostponeTrainingsUntilNPlus6Command, \
    PostponeMiniTrainingsUntilNPlus6Command
from education_group.ddd.service.write import postpone_trainings_until_n_plus_6_service, \
    postpone_groups_until_n_plus_6_service, postpone_mini_trainings_until_n_plus_6_service
from education_group.cms.postponement import bulk_postpone_cms_for_education_group_year, \
    bulk_postpone_cms_for_group_year
from education_group.models.group_year import GroupYear
from program_management.ddd.command import PostponeProgramTreesUntilNPlus6Command, \
    PostponeProgramTreeVersionsUntilNPlus6Command
from program_management.ddd.service.write import postpone_program_trees_until_n_plus_6_service, \
    postpone_program_tree_versions_until_n_plus_6_service


@celery_app.task
def run() -> dict:
    programs_created = postpone_program_trees_until_n_plus_6_service.postpone_program_trees_until_n_plus_6(
        PostponeProgramTreesUntilNPlus6Command()
    )
    trainings_created = postpone_trainings_until_n_plus_6_service.postpone_trainings_until_n_plus_6(
        PostponeTrainingsUntilNPlus6Command()
    )
    mini_trainings_created = postpone_mini_trainings_until_n_plus_6_service.postpone_minitrainings_until_n_plus_6(
        PostponeMiniTrainingsUntilNPlus6Command()
    )
    program_versions_created = postpone_program_tree_versions_until_n_plus_6_service. \
        postpone_program_tree_versions_until_n_plus_6(
            PostponeProgramTreeVersionsUntilNPlus6Command()
        )

    highest_year = max([program.year for program in programs_created])
    postpone_to_n_publication_datas(highest_year)
    return {
        "trainings": [str(training_identity) for training_identity in trainings_created],
        "mini_trainings": [str(mini_training_identity) for mini_training_identity in mini_trainings_created],
        "program": [str(program_identity) for program_identity in programs_created],
        "program_versions": [str(program_version_identity) for program_version_identity in program_versions_created],
    }


def postpone_to_n_publication_datas(to_year: int):
    education_group_year_qs = EducationGroupYear.objects.filter(academic_year__year=to_year-1)
    group_year_qs = GroupYear.objects.filter(academic_year__year=to_year-1)

    _postpone_until_n_plus_6_publication_datas(education_group_year_qs, group_year_qs)


def _postpone_until_n_plus_6_publication_datas(education_group_year_qs, group_year_qs):
    bulk_postpone_cms_for_education_group_year(education_group_year_qs)
    bulk_postpone_cms_for_group_year(group_year_qs)

    bulk_postpone_access_requirements(education_group_year_qs)
    bulk_postpone_access_requirements_line(education_group_year_qs)

    bulk_postpone_publication_contact(education_group_year_qs)
    bulk_postpone_publication_entity(education_group_year_qs)

    bulk_postpone_achievements(education_group_year_qs)
