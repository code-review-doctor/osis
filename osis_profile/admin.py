from django.contrib import admin

from osis_profile.models import BelgianHighSchoolDiploma, ForeignHighSchoolDiploma
from osis_profile.models.education import LanguageKnowledge, Schedule


class HighSchoolDiplomaAdmin(admin.ModelAdmin):
    autocomplete_fields = ["person"]


class LanguageKnowledgeAdmin(admin.ModelAdmin):
    autocomplete_fields = ["person", "language"]


admin.site.register(BelgianHighSchoolDiploma, HighSchoolDiplomaAdmin)
admin.site.register(ForeignHighSchoolDiploma, HighSchoolDiplomaAdmin)
admin.site.register(Schedule)
admin.site.register(LanguageKnowledge, LanguageKnowledgeAdmin)
