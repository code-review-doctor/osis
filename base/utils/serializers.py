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
import copy
import datetime
import typing
from collections import OrderedDict
from decimal import Decimal
from uuid import UUID

import attr
from rest_framework import serializers

from base.models.utils.utils import ChoiceEnum
from osis_common.ddd.interface import CommandRequest, DTO, EntityIdentity


class DTOSerializer(serializers.Serializer):
    """
    A `DTOSerializer` is just a regular `Serializer`, except that:

    * A set of default fields are automatically populated from the Meta.source dataclass.
    * All fields are set to read-only if needed when Meta.read_only is True.
    """

    serializer_field_mapping = {
        bool: serializers.BooleanField,
        int: serializers.IntegerField,
        str: serializers.CharField,
        Decimal: serializers.DecimalField,
        datetime.date: serializers.DateField,
        datetime.datetime: serializers.DateTimeField,
        datetime.time: serializers.TimeField,
        UUID: serializers.UUIDField,
    }

    def get_fields(self):
        """
        Return the dict of field names -> field instances that should be
        used for `self.fields` when instantiating the serializer.
        """
        assert hasattr(self, 'Meta'), (
            'Class {serializer_class} missing "Meta" attribute'.format(
                serializer_class=self.__class__.__name__
            )
        )
        meta = getattr(self, 'Meta')
        assert hasattr(meta, 'source'), (
            'Class {serializer_class} missing "Meta.source" attribute'.format(
                serializer_class=self.__class__.__name__
            )
        )

        declared_fields = copy.deepcopy(getattr(self, '_declared_fields'))
        source = meta.source

        # Retrieve metadata about fields & relationships on the source class.
        fields_info = attr.fields(source)

        # Determine any extra field arguments and hidden fields that
        # should be included
        extra_kwargs = self.get_extra_kwargs()

        # Determine the fields that should be included on the serializer.
        fields = OrderedDict()

        for field in fields_info:
            # If the field comes from CommandRequest then do not take it.
            if issubclass(source, CommandRequest) and field.name == 'transaction_id':
                continue

            # If the field is explicitly declared as None on the class then do not take it.
            if getattr(self, field.name, False) is None:
                continue

            # If the field is explicitly declared on the class then use that.
            if field.name in declared_fields:
                fields[field.name] = declared_fields[field.name]
                continue

            extra_field_kwargs = extra_kwargs.get(field.name, {})

            # Determine the serializer field class and keyword arguments.
            field_class, field_kwargs = self.build_field(field)

            # Include any kwargs defined in `Meta.extra_kwargs`
            field_kwargs = self.include_extra_kwargs(
                field_kwargs, extra_field_kwargs
            )

            # Create the serializer field.
            fields[field.name] = field_class(**field_kwargs)

        return fields

    # Determine the fields to apply...

    def build_field(self, source_field):
        """
        Return a two tuple of (cls, kwargs) to build a serializer field with.
        """
        field_class, field_kwargs = self.get_field_type(source_field.type)

        return field_class, field_kwargs

    # Methods for constructing serializer fields...

    def get_field_type(self, field_type):
        field_kwargs = {}
        field_mapping = self.serializer_field_mapping

        # Check if it is optional
        # FIXME use get_origin() on python3.8
        if (getattr(field_type, '__origin__', None) is typing.Union
                and len(field_type.__args__) == 2
                and field_type.__args__[-1] is type(None)):
            field_class = field_mapping[field_type.__args__[0]]
            field_kwargs['required'] = False
            if field_type.__args__[0] == str:
                field_kwargs['allow_blank'] = True
            else:
                field_kwargs['allow_null'] = True
        elif getattr(field_type, '__origin__', None) is list:
            field_class = serializers.ListField
            field_kwargs['child'] = self.get_field_type(field_type.__args__[0])[0]()
        elif isinstance(field_type, ChoiceEnum):
            field_class = serializers.ChoiceField
            field_kwargs['choices'] = field_type.choices()
        elif issubclass(field_type, (DTO, EntityIdentity)):
            field_class = self.get_nested_serializer(field_type)
        # TODO for Union, convert to ReadOnlyField, custom mapping or not supported
        else:
            try:
                field_class = field_mapping[field_type]
            except KeyError:
                raise NotImplementedError('{} serializer mapping not implemented'.format(field_type))
        return field_class, field_kwargs

    def include_extra_kwargs(self, kwargs, extra_kwargs):
        """
        Include any 'extra_kwargs' that have been included for this field,
        possibly removing any incompatible existing keyword arguments.
        """
        meta = getattr(self, 'Meta')
        read_only_fields = getattr(meta, 'read_only', None)
        if read_only_fields is True:
            extra_kwargs['read_only'] = True

        if extra_kwargs.get('read_only', False):
            for attribute in [
                'required', 'default', 'allow_blank', 'allow_null',
                'min_length', 'max_length', 'min_value', 'max_value',
                'validators', 'queryset'
            ]:
                kwargs.pop(attribute, None)

        if extra_kwargs.get('default') and kwargs.get('required') is False:
            kwargs.pop('required')

        if extra_kwargs.get('read_only', kwargs.get('read_only', False)):
            extra_kwargs.pop('required', None)  # Read only fields should always omit the 'required' argument.

        kwargs.update(extra_kwargs)

        return kwargs

    def get_extra_kwargs(self):
        """
        Return a dictionary mapping field names to a dictionary of
        additional keyword arguments.
        """
        meta = getattr(self, 'Meta')
        extra_kwargs = copy.deepcopy(getattr(meta, 'extra_kwargs', {}))

        read_only_fields = getattr(meta, 'read_only', None)
        if read_only_fields is not None:
            if not isinstance(read_only_fields, (list, tuple)):
                raise TypeError(
                    'The `read_only_fields` option must be a list or tuple. '
                    'Got %s.' % type(read_only_fields).__name__
                )
            for field_name in read_only_fields:
                kwargs = extra_kwargs.get(field_name, {})
                kwargs['read_only'] = True
                extra_kwargs[field_name] = kwargs

        return extra_kwargs

    def create(self, validated_data):
        raise NotImplementedError("This serializer should not be used for writing purposes")

    def update(self, instance, validated_data):
        raise NotImplementedError("This serializer should not be used for writing purposes")

    @staticmethod
    def get_nested_serializer(dto_class):
        class NestedSerializer(DTOSerializer):
            class Meta:
                source = dto_class

        return NestedSerializer
