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
from collections import defaultdict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import exception_handler

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from osis_common.ddd.interface import BusinessException


def handle(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, MultipleBusinessExceptions):
        field_name_by_exception = context.get('field_name_by_exception', {})
        data = defaultdict(list)

        for exception in exc.exceptions:
            exception_formated = __format_exception(exception)

            field_names = field_name_by_exception.get(type(exception), [])
            if field_names:
                errors_dict = dict.fromkeys(field_names, [exception_formated])
                data = {field: exceptions + data[field] for field, exceptions in errors_dict.items()}
            else:
                data.setdefault(api_settings.NON_FIELD_ERRORS_KEY, []).append(exception_formated)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    return response


def __format_exception(exception: BusinessException):
    return {
        "status_code": getattr(exception, 'status_code', None),
        "detail": exception.message
    }
