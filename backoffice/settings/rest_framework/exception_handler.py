from collections import defaultdict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import exception_handler

from base.ddd.utils.business_validator import MultipleBusinessExceptions


def handle(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, MultipleBusinessExceptions):
        field_name_by_exception = context.get('field_name_by_exception', {})
        data = defaultdict(list)

        for exception in exc.exceptions:
            field_names = field_name_by_exception.get(type(exception), [])
            if field_names:
                errors_dict = dict.fromkeys(field_names, [exception.message])
                data = {field: exceptions + data[field] for field, exceptions in errors_dict.items()}
            else:
                data[api_settings.NON_FIELD_ERRORS_KEY].append(exception.message)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    return response
