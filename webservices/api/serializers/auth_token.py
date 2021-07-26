##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.conf import settings
from django.contrib.auth import backends
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from base.models.person import Person


class AuthPersonSerializer(serializers.Serializer):
    global_id = serializers.CharField(required=True)
    gender = serializers.ChoiceField(choices=Person.GENDER_CHOICES, required=False, default='U')
    first_name = serializers.CharField(required=False, allow_blank=True)
    middle_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    phone_mobile = serializers.CharField(required=False, allow_blank=True)
    language = serializers.ChoiceField(choices=settings.LANGUAGES, required=False, default=settings.LANGUAGE_CODE)


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"), required=True)
    person = AuthPersonSerializer(required=True)
    force_user_creation = serializers.BooleanField(label=_("Create user if not exists"), default=False)

    def validate(self, attrs):
        UserModel = backends.get_user_model()
        user_kwargs = {UserModel.USERNAME_FIELD: attrs['username']}

        if attrs['force_user_creation']:
            user, created = UserModel.objects.get_or_create(**user_kwargs)
        else:
            try:
                user = UserModel.objects.get(**user_kwargs)
            except UserModel.DoesNotExist:
                msg = _('Unable to find username provided.')
                raise serializers.ValidationError({'username': msg})

        # Create/Update person according to data send by certified requester...
        person_payload = attrs['person']
        Person.objects.update_or_create(
            global_id=person_payload['global_id'],
            defaults={
                'user_id': user.pk,
                'gender': person_payload['gender'] or '',
                'first_name': person_payload['first_name'] or '',
                'middle_name': person_payload['middle_name'] or '',
                'last_name': person_payload['last_name'] or '',
                'email': person_payload['email'] or '',
                'phone': person_payload['phone'] or '',
                'phone_mobile': person_payload['phone_mobile'] or '',
                'language': person_payload['language'] or '',
            }
        )
        attrs['user'] = user
        return attrs
