from django.contrib import admin

from osis_profile.models import BelgianHighSchoolDiploma, ForeignHighSchoolDiploma
from osis_profile.models.education import Schedule


class HighSchoolDiplomaAdmin(admin.ModelAdmin):
    autocomplete_fields = ["person"]


admin.site.register(BelgianHighSchoolDiploma, HighSchoolDiplomaAdmin)
admin.site.register(ForeignHighSchoolDiploma, HighSchoolDiplomaAdmin)
admin.site.register(Schedule)
