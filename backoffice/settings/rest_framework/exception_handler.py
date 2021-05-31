from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from base.ddd.utils.business_validator import MultipleBusinessExceptions


def handle(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, MultipleBusinessExceptions):
        # TODO: Allow mapping between field and error
        data = {
            'non_field_errors': [business_exception.message for business_exception in exc.exceptions]
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    return response
