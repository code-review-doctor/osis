from django_filters import OrderingFilter
from django_filters.constants import EMPTY_VALUES


class OrderingFilterWithDefault(OrderingFilter):
    """
    This filter override OrderingFilter in order to provide the default ordering capability
    """
    def __init__(self, *args, **kwargs):
        self.default_ordering = kwargs.pop('default_ordering', None)
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value in EMPTY_VALUES and self.default_ordering:
            return qs.order_by(*self.default_ordering)
        return super().filter(qs, value)


class MultipleColumnOrderingFilter(OrderingFilter):
    """
    This filter accepts single field names that map multiple ordering fields
    e.g. to concat first_name and last_name in full_name, init ordering map with fields=(
            ...
            ('last_name', 'last_name'),
            ('first_name', 'first_name'),
            (('last_name', 'first_name'), 'full_name'),
            ...
        )
    """
    def get_ordering_value(self, param):
        descending = param.startswith('-')
        param = param[1:] if descending else param
        field_names = self.param_map.get(param, param)
        if isinstance(field_names, tuple):
            return ["-%s" % field_name if descending else field_name for field_name in field_names]
        return "-%s" % field_names if descending else field_names

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        return qs.order_by(*self.map_multiple_ordering_values(value))

    def map_multiple_ordering_values(self, value):
        ordering = []
        for v in value:
            if isinstance(self.param_map[v.lstrip('-')], tuple):
                ordering.extend(self.get_ordering_value(v))
                continue
            ordering.append(v)
        return ordering
