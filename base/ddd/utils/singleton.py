# ##############################################################################
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
# ##############################################################################
from abc import ABCMeta
import os
import inspect


class SingletonMeta(ABCMeta):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        # To prevent case repositories class have same name than other repositories class in other contexts
        abs_path_to_class = os.path.abspath(inspect.getfile(cls)) + cls.__name__
        if cls not in cls._instance:
            cls._instance[abs_path_to_class] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instance[abs_path_to_class]
