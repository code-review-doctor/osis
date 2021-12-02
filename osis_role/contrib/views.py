from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
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
        Returns the message related to the first invalid permission, otherwise returns None.
        Raises an exception if the user is not authenticated.
        """
        if not user.is_authenticated:
            # No user, don't check permission
            raise drf_exceptions.NotAuthenticated()

        request_permissions = self.permission_mapping.get(method)

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
                permission_error = get_permission_error(user, permission)
                return permission_error if permission_error is not None else _("Method '{}' not allowed".format(method))

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        failed_permission_message = self.check_method_permissions(request.user, request.method)
        if failed_permission_message is not None:
            raise drf_exceptions.PermissionDenied(failed_permission_message)

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
