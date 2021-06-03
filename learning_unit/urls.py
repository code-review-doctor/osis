from django.urls import include, path

from learning_unit.views.learning_unit_class.identification_read import ClassIdentificationView

urlpatterns = [
    path('<int:learning_unit_year>/<str:learning_unit_code>/', include([
        path('class/<str:class_code>/', include([
            path('identification', ClassIdentificationView.as_view(), name='class_identification'),
        ]))
    ]))
]
