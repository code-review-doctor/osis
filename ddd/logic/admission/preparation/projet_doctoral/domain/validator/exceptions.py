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

from django.utils.translation import gettext_lazy as _

from osis_common.ddd.interface import BusinessException


class MaximumPropositionsAtteintException(BusinessException):
    def __init__(self, **kwargs):
        message = _("You've reached the maximum authorized propositions.")
        super().__init__(message, **kwargs)


class DoctoratNonTrouveException(BusinessException):
    def __init__(self, **kwargs):
        message = _("No PhD found.")
        super().__init__(message, **kwargs)


class PropositionNonTrouveeException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Proposition not found.")
        super().__init__(message, **kwargs)


class GroupeDeSupervisionNonTrouveException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Supervision group not found.")
        super().__init__(message, **kwargs)


class BureauCDEInconsistantException(BusinessException):
    def __init__(self, **kwargs):
        message = _("CDE Bureau should be filled in only if the doctorate's entity is CDE")
        super().__init__(message, **kwargs)


class ContratTravailInconsistantException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Work contract should be set when financing type is set to work contract")
        super().__init__(message, **kwargs)


class InstitutionInconsistanteException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Institution should be set when PhD has been set to yes or partial")
        super().__init__(message, **kwargs)


class MembreGroupeDeSupervisionNonTrouveException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Supervision group member not found.")
        super().__init__(message, **kwargs)


class PromoteurNonTrouveException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Promoter not found.")
        super().__init__(message, **kwargs)


class MembreCANonTrouveException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Membre CA not found.")
        super().__init__(message, **kwargs)


class SignataireNonTrouveException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Member of supervision group not found.")
        super().__init__(message, **kwargs)


class SignataireDejaInviteException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Member of supervision group already invited.")
        super().__init__(message, **kwargs)


class SignatairePasInviteException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Member of supervision group not invited.")
        super().__init__(message, **kwargs)


class DejaPromoteurException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Already a promoter.")
        super().__init__(message, **kwargs)


class DejaMembreCAException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Already a member of CA.")
        super().__init__(message, **kwargs)
