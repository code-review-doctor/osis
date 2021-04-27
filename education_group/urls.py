from django.urls import include, path, register_converter

from education_group.converters import GroupTypeConverter, TrainingTypeConverter, MiniTrainingTypeConverter, \
    AcronymConverter, MiniTrainingAcronymConverter
from education_group.views import group, training, mini_training, general_information, access_requirements, \
    publication_contact, achievement
from education_group.views.autocomplete import EducationGroupTypeAutoComplete, CertificateAimAutocomplete
from education_group.views.configuration.common_list import CommonListView
from education_group.views.configuration.home import ConfigurationHomeView
from education_group.views.mini_training.delete import MiniTrainingDeleteView
from education_group.views.proxy.read import ReadEducationGroupRedirectView
from education_group.views.training.delete import TrainingDeleteView
from education_group.views.training.update import TrainingUpdateView

register_converter(GroupTypeConverter, 'group_type')
register_converter(MiniTrainingTypeConverter, 'mini_training_type')
register_converter(TrainingTypeConverter, 'training_type')
register_converter(AcronymConverter, 'acronym')
register_converter(MiniTrainingAcronymConverter, 'mini_training_acronym')

urlpatterns = [
    path('groups/', include([
        path('<group_type:type>/create', group.GroupCreateView.as_view(), name='group_create'),
        path('<int:year>/<str:code>/', include([
            path('update/', group.GroupUpdateView.as_view(), name='group_update'),
            path('identification/', group.GroupReadIdentification.as_view(), name='group_identification'),
            path('content/', group.GroupReadContent.as_view(), name='group_content'),
            path('utilization/', group.GroupReadUtilization.as_view(), name='group_utilization'),
            path('general_information/', include([
                path('read/', group.GroupReadGeneralInformation.as_view(), name='group_general_information'),
                path('update/', group.GroupUpdateGeneralInformation.as_view(), name='group_general_information_update'),
            ])),
            path('delete/', group.GroupDeleteView.as_view(), name='group_delete')
        ]))
    ])),
    path('mini_trainings/', include([
        path('<mini_training_type:type>/create', mini_training.MiniTrainingCreateView.as_view(),
             name='mini_training_create'),
        path('<int:year>/<str:code>/', include([
            path(
                'identification/',
                mini_training.MiniTrainingReadIdentification.as_view(),
                name='mini_training_identification'
            ),
            path('general_information/', include([
                path(
                    'read/', mini_training.MiniTrainingReadGeneralInformation.as_view(),
                    name='mini_training_general_information'
                ),
                path(
                    'update/',
                    mini_training.MiniTrainingUpdateGeneralInformation.as_view(),
                    name='mini_training_general_information_update'
                ),
            ])),
            path('create/', achievement.CreateEducationGroupAchievement.as_view(),
                 name='minitraining_achievement_create'),
            path('delete/', MiniTrainingDeleteView.as_view(), name='mini_training_delete'),
            path('<int:education_group_achievement_pk>/', include([
                path('actions/', achievement.EducationGroupAchievementAction.as_view(),
                     name='minitraining_achievement_actions'),
                path('create/', achievement.CreateEducationGroupDetailedAchievement.as_view(),
                     name='minitraining_detailed_achievement_create'),
                path('delete/', achievement.DeleteEducationGroupAchievement.as_view(),
                     name='minitraining_achievement_delete'),
                path('update/', achievement.UpdateEducationGroupAchievement.as_view(),
                     name='minitraining_achievement_update'),
                path('<int:education_group_detail_achievement_pk>/', include([
                    path('actions/',
                         achievement.EducationGroupDetailedAchievementAction.as_view(),
                         name='minitraining_detailed_achievement_actions'),
                    path('delete/', achievement.DeleteEducationGroupDetailedAchievement.as_view(),
                         name='minitraining_detailed_achievement_delete'),
                    path('update/', achievement.UpdateEducationGroupDetailedAchievement.as_view(),
                         name='minitraining_detailed_achievement_update'),
                ]))
            ])),
            path('<mini_training_acronym:acronym>/update/', mini_training.MiniTrainingUpdateView.as_view(),
                 name='mini_training_update'),
            path('content/', mini_training.MiniTrainingReadContent.as_view(), name='mini_training_content'),
            path('utilization/', mini_training.MiniTrainingReadUtilization.as_view(), name='mini_training_utilization'),
            path(
                'skills_achievements/',
                mini_training.MiniTrainingReadSkillsAchievements.as_view(),
                name='mini_training_skills_achievements'
            ),
            path(
                'admission_conditions/',
                mini_training.MiniTrainingReadAccessRequirements.as_view(),
                name='mini_training_access_requirements'
            ),
        ])),
    ])),
    path('mini_trainings/<int:year>/<str:code>/', include([
        path(
            'identification/',
            mini_training.MiniTrainingReadIdentification.as_view(),
            name='mini_training_identification'
        ),
        path('content/', mini_training.MiniTrainingReadContent.as_view(), name='mini_training_content'),
        path('utilization/', mini_training.MiniTrainingReadUtilization.as_view(), name='mini_training_utilization'),
        path(
            'skills_achievements/',
            mini_training.MiniTrainingReadSkillsAchievements.as_view(),
            name='mini_training_skills_achievements'
        ),
        path(
            'admission_conditions/',
            mini_training.MiniTrainingReadAccessRequirements.as_view(),
            name='mini_training_access_requirements'
        ),
    ])),
    path('trainings/', include([
        path('<training_type:type>/create/', training.TrainingCreateView.as_view(), name='training_create'),
        path('<int:year>/<str:code>/', include([  # FIXME use acronym
            path('general_information/', include([
                path('read/', training.TrainingReadGeneralInformation.as_view(), name='training_general_information'),
                path(
                    'update/',
                    training.TrainingUpdateGeneralInformation.as_view(),
                    name='training_general_information_update'
                ),
            ])),
            path('<acronym:title>/update/', TrainingUpdateView.as_view(), name='training_update'),
            path('create/', achievement.CreateEducationGroupAchievement.as_view(), name='training_achievement_create'),
            path('delete/', TrainingDeleteView.as_view(), name='training_delete'),
            path('achievement/<int:education_group_achievement_pk>/', include([
                path('actions/', achievement.EducationGroupAchievementAction.as_view(),
                     name='training_achievement_actions'),
                path('create/', achievement.CreateEducationGroupDetailedAchievement.as_view(),
                     name='training_detailed_achievement_create'),
                path('delete/', achievement.DeleteEducationGroupAchievement.as_view(),
                     name='training_achievement_delete'),
                path('update/', achievement.UpdateEducationGroupAchievement.as_view(),
                     name='training_achievement_update'),
                path('<int:education_group_detail_achievement_pk>/', include([
                    path('actions/',
                         achievement.EducationGroupDetailedAchievementAction.as_view(),
                         name='training_detailed_achievement_actions'),
                    path('delete/', achievement.DeleteEducationGroupDetailedAchievement.as_view(),
                         name='training_detailed_achievement_delete'),
                    path('update/', achievement.UpdateEducationGroupDetailedAchievement.as_view(),
                         name='training_detailed_achievement_update'),
                ]))
            ])),
            path('identification/', training.TrainingReadIdentification.as_view(), name='training_identification'),
            path('diplomas/', training.TrainingReadDiplomaCertificate.as_view(), name='training_diplomas'),
            path(
                'administrative_data/',
                training.TrainingReadAdministrativeData.as_view(),
                name='training_administrative_data'
            ),
            path('content/', training.TrainingReadContent.as_view(), name='training_content'),
            path('utilization/', training.TrainingReadUtilization.as_view(), name='training_utilization'),

            path(
                'skills_achievements/',
                training.TrainingReadSkillsAchievements.as_view(),
                name='training_skills_achievements'
            ),
            path(
                'admission_conditions/',
                training.TrainingReadAccessRequirements.as_view(),
                name='training_access_requirements'
            ),
        ])),
    ])),
    path('general_information/<int:year>/', include([
        path('common/', include([
            path('', general_information.CommonGeneralInformation.as_view(), name="common_general_information"),
            path(
                'update',
                general_information.UpdateCommonGeneralInformation.as_view(),
                name="update_common_general_information"
            ),
            path('publish', general_information.publish_common_pedagogy, name="publish_common_general_information"),
        ])),
        path('common-bachelor/', include([
            path(
                '',
                general_information.CommonBachelorAccessRequirements.as_view(),
                name="common_bachelor_access_requirements"
            ),
            path(
                'publish',
                general_information.publish_common_access_requirements,
                {'redirect_view': 'common_bachelor_access_requirements'},
                name="publish_common_bachelor_access_requirements"
            ),
        ])),
        path('common-aggregate/', include([
            path(
                '',
                general_information.CommonAggregateAccessRequirements.as_view(),
                name="common_aggregate_access_requirements"
            ),
            path(
                'publish',
                general_information.publish_common_access_requirements,
                {'redirect_view': 'common_aggregate_access_requirements'},
                name="publish_common_aggregate_access_requirements"
            ),
        ])),
        path('common-master/', include([
            path(
                '',
                general_information.CommonMasterAccessRequirements.as_view(),
                name="common_master_access_requirements"
            ),
            path(
                'publish',
                general_information.publish_common_access_requirements,
                {'redirect_view': 'common_master_access_requirements'},
                name="publish_common_master_access_requirements"
            ),
        ])),
        path('common-master-specialized/', include([
            path(
                '',
                general_information.CommonMasterSpecializedAccessRequirements.as_view(),
                name="common_master_specialized_access_requirements"
            ),
            path(
                'publish',
                general_information.publish_common_access_requirements,
                {'redirect_view': 'common_master_specialized_access_requirements'},
                name="publish_common_master_specialized_access_requirements"
            ),
        ])),
    ])),
    path('<int:year>/<acronym:acronym>/', ReadEducationGroupRedirectView.as_view(), name='education_group_read_proxy'),
    path('<int:year>/<acronym:code>/', include([
        path('', ReadEducationGroupRedirectView.as_view(), name='education_group_read_proxy'),
        path(
            'admission_conditions/remove_line',
            access_requirements.DeleteAccessRequirementsLine.as_view(),
            name='education_group_year_access_requirements_remove_line'),

        path(
            'admission_conditions/update_line',
            access_requirements.UpdateAccessRequirementsLine.as_view(),
            name='education_group_year_access_requirements_update_line'),

        path(
            'admission_conditions/create_line',
            access_requirements.CreateAccessRequirementsLine.as_view(),
            name='education_group_year_access_requirements_create_line'),

        path(
            'admission_conditions/update_text',
            access_requirements.UpdateAccessRequirements.as_view(),
            name='education_group_year_access_requirements_update_text'),

        path(
            'admission_conditions/line/order',
            access_requirements.OrderAccessRequirementsLine.as_view(),
            name='education_group_year_access_requirements_line_order'),
        path(
            'admission_conditions/lang/edit/<str:language>/',
            access_requirements.change_language,
            name='tab_lang_edit'),
        path(
            'publication_contact/<int:education_group_year_id>/',
            include([
                path('edit_entity/',
                     publication_contact.UpdateEducationGroupEntityPublicationContactView.as_view(),
                     name='publication_contact_entity_edit'),
            ])),
        path('publication_contact/', include([
            path('create/',
                 publication_contact.CreateEducationGroupPublicationContactView.as_view(),
                 name="publication_contact_create"),
            path('edit/<int:publication_contact_id>/',
                 publication_contact.UpdateEducationGroupPublicationContactView.as_view(),
                 name="publication_contact_edit"),
            path('delete/<int:publication_contact_id>/',
                 publication_contact.EducationGroupPublicationContactDeleteView.as_view(),
                 name="publication_contact_delete"),
        ])),
    ])),
    path('configuration/', include([
        path('home/', ConfigurationHomeView.as_view(), name='catalog_configuration'),
        path('common-topics/', CommonListView.as_view(), name='common_topics_configuration'),
    ])),
    path('autocomplete/', include([
        path(
            'education-group-types/',
            EducationGroupTypeAutoComplete.as_view(),
            name='education_group_type_autocomplete'
        ),
        path('certificate-aims/', CertificateAimAutocomplete.as_view(), name='certificate_aim_autocomplete'),
    ])),
]
