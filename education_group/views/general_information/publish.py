from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from base.views.common import display_error_messages, display_success_messages
from education_group.ddd import command
from education_group.ddd.service.write import publish_common_pedagogy_service, \
    publish_common_access_requirements_service
from education_group.ddd.service.write.publish_common_access_requirements_service import \
    PublishCommonAccessRequirementsException
from education_group.ddd.service.write.publish_common_pedagogy_service import PublishCommonPedagogyException


@login_required
@require_http_methods(['POST'])
def publish_common_access_requirements(request, year, redirect_view):
    try:
        cmd = command.PublishCommonAccessRequirementsCommand(year=year)
        publish_common_access_requirements_service.publish_common_access_requirements(cmd)
        display_success_messages(request, _('Common access requirements will be published soon'))
    except PublishCommonAccessRequirementsException as e:
        display_error_messages(request, e.message)
    return HttpResponseRedirect(reverse(redirect_view, kwargs={'year': year}))


@login_required
@require_http_methods(['POST'])
def publish_common_pedagogy(request, year):
    try:
        cmd = command.PublishCommonPedagogyCommand(year=year)
        publish_common_pedagogy_service.publish_common_pedagogy(cmd)
        display_success_messages(request, _('Common general informations will be published soon'))
    except PublishCommonPedagogyException as e:
        display_error_messages(request, e.message)
    return HttpResponseRedirect(reverse('common_general_information', kwargs={'year': year}))
