from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.decorators import method_decorator
import rest_framework.exceptions as drf_exceptions
from rules.contrib.views import PermissionRequiredMixin as PermissionRequiredMixinRules, \
    objectgetter as objectgetterrules, \
    permission_required as permission_requiredrules

# Wraps django-rules
from osis_role.errors import get_permission_error

objectgetter = objectgetterrules
permission_required = permission_requiredrules


class PermissionRequiredMixin(PermissionRequiredMixinRules):
    def handle_no_permission(self):
        """
        Override default django behaviour, if user is not authenticated, redirect to login page
        """
        if not self.request.user.is_authenticated:
            return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())
        super().handle_no_permission()


class APIPermissionRequiredMixin:

    permission_mapping = {}

    def check_method_permissions(self, user, method):
        """
        Check that a user has the right to use a method.
        Raises an appropriate exception if this is not the case.
        """
        request_permissions = self.permission_mapping.get(method)

        if not user.is_authenticated:
            raise drf_exceptions.NotAuthenticated()

        if request_permissions is None:
            # No permission is specified for this request then we skip the checking
            return

        if isinstance(request_permissions, str):
            request_permissions = (request_permissions, )

        # Eventually get the object to check for permission against
        obj = self.get_permission_object()

        # Check the permissions
        for permission in request_permissions:
            if not user.has_perm(permission, obj):
                raise drf_exceptions.PermissionDenied(get_permission_error(user, permission))

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        return self.check_method_permissions(request.user, request.method)

    def get_permission_object(self):
        """
        Override this method to provide the object to check for permission against.
        """
        return None


class AjaxPermissionRequiredMixin(PermissionRequiredMixinRules):

    permission_required = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            error_msg = self.get_permission_error(request)
            if request.is_ajax():
                return render(request, 'education_group/blocks/modal/modal_access_denied.html', {
                    'access_message': error_msg
                })
            else:
                raise PermissionDenied(error_msg)
        return super().dispatch(request, *args, **kwargs)

    def get_permission_error(self, request) -> str:
        return get_permission_error(request.user, self.permission_required)
