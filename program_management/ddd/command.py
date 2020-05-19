##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
import collections

from django.contrib.auth import models

from osis_common.ddd import interface


class DetachNodeCommand(interface.CommandRequest):
    # To implement
    pass


class OrderLinkCommand(interface.CommandRequest):
    # To implement
    pass


class CreateProgramTreeVersionCommand(interface.CommandRequest):
    # To implement
    pass


class CopyElementCommand(interface.CommandRequest):
    def __init__(self, user: models.User, element_id: int, element_type: str):
        self.user = user
        self.element_id = element_id
        self.element_type = element_type


class CutElementCommand(interface.CommandRequest):
    def __init__(self, user: models.User, element_id: int, element_type: str, link_id: int):
        self.user = user
        self.element_id = element_id
        self.element_type = element_type
        self.link_id = link_id


AttachNodeCommand = collections.namedtuple(
    "AttachNodeCommand",
    "root_id, node_id_to_attach, type_of_node_to_attach, path_where_to_attach, commit,"
    " access_condition, is_mandatory, block, link_type, comment, comment_english, relative_credits"
)

CheckAttachNodeCommand = collections.namedtuple(
    "CheckAttachNodeCommand",
    "root_id, nodes_to_attach, path_where_to_attach"
)
