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
from django.urls import include, path

from learning_unit.views.learning_unit_class.create import CreateClassView as CreateClass
from learning_unit.views.learning_unit_class.identification_read import ClassIdentificationView
from learning_unit.views.learning_unit_class.learning_unit_tutors import LearningUnitTutorsView
from learning_unit.views.learning_unit_class.tutor_repartition import TutorRepartitionView, TutorRepartitionRemoveView
from learning_unit.views.learning_unit_class.tutors import ClassTutorsView
from learning_unit.views.learning_unit_class.update import UpdateClassView as UpdateClass

urlpatterns = [
    path('<int:learning_unit_year>/<str:learning_unit_code>/', include([
        path('class/', include([
            path('create', CreateClass.as_view(), name='class_create'),
        ])),
        path('class/<str:class_code>/', include([
            path('identification', ClassIdentificationView.as_view(), name='class_identification'),
            path('tutors', ClassTutorsView.as_view(), name='class_tutors'),
            path('update', UpdateClass.as_view(), name='class_update'),
            path('lu_tutors', LearningUnitTutorsView.as_view(), name='learning_unit_tutors'),
            path('tutors/<str:attribution_uuid>/repartition',
                 TutorRepartitionView.as_view(), name='edit_charge_repartition'),
            path('tutors/<str:attribution_uuid>/repartition/remove',
                 TutorRepartitionRemoveView.as_view(), name='remove_class_attribution'),
        ]))
    ]))
]
