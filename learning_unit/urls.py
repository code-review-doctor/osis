from django.urls import include, path

from learning_unit.views.learning_unit_class.identification_read import ClassIdentitificationView

urlpatterns = [
    path('<int:learning_unit_year>/<str:learning_unit_code>/', include([
        path('class/<str:class_code>/', include([
            path('identification', ClassIdentitificationView.as_view(), name='class_identification'),
        ]))
    ]))
]
