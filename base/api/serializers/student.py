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
from rest_framework import serializers

from base.api.serializers.person import PersonDetailSerializer
from base.models.student import Student
from django.urls import reverse


class StudentListSerializer(serializers.Serializer):
    registration_id = serializers.CharField()
    name = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    select_url = serializers.SerializerMethodField()

    def get_name(self, obj):
        return str(obj.person)

    def get_gender(self, obj):
        return obj.person.gender

    def get_select_url(self, obj):
        return reverse(
            "student_read",
            kwargs={'student_id': obj.id}
        )


class StudentSerializer(serializers.ModelSerializer):
    person = PersonDetailSerializer()

    class Meta:
        model = Student
        fields = (
            'uuid',
            'registration_id',
            'person',
        )
