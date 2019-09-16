##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from rest_framework import serializers


class DynamicLanguageFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `lang` argument that
    controls which fields should be displayed depending on the language.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'lang' arg up to the superclass
        language = kwargs.pop('lang', None)

        # Instantiate the superclass normally
        super(DynamicLanguageFieldsModelSerializer, self).__init__(*args, **kwargs)

        if language is not None:
            keys_list = list(self.fields.keys())
            keys_list.remove('alert_message')
            for field_name in keys_list:
                if language == settings.LANGUAGE_CODE_FR and settings.LANGUAGE_CODE_EN in field_name:
                    self.fields.pop(field_name)
                elif language == settings.LANGUAGE_CODE_EN not in field_name:
                    self.fields.pop(field_name)
