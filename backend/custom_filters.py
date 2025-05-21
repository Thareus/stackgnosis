from django_filters.filters import NumericRangeFilter, MultipleChoiceFilter, ModelChoiceFilter, ModelMultipleChoiceFilter
from django_filters.constants import EMPTY_VALUES

from .custom_form_fields import (
    CustomNumericRangeField, Select2MultipleChoiceField, Select2ModelChoiceField,
    Select2ModelMultipleChoiceField
)

### FILTER CLASSES ###
class CustomNumericRangeFilter(NumericRangeFilter):
    field_class = CustomNumericRangeField

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        if value:
            if value[0] is not None and value[1] is not None:
                self.lookup_expr = "range"
                value = (value[0], value[1])
            elif value[0] is not None:
                self.lookup_expr = "gt"
                value = value[0]
            elif value[1] is not None:
                self.lookup_expr = "lt"
                value = value[1]
        if self.distinct:
            qs = qs.distinct()
        lookup = "%s__%s" % (self.field_name, self.lookup_expr)
        qs = self.get_method(qs)(**{lookup: value})
        return qs

class Select2ModelChoiceFilter(ModelChoiceFilter):
    field_class = Select2ModelChoiceField

class Select2MultipleChoiceFilter(MultipleChoiceFilter):
    field_class = Select2MultipleChoiceField

    def to_python(self, value):
        """
        Overrides method to accomodate singular values instead of raising ValidationError
        """
        if not value:
            return []
        elif isinstance(value, str): # Singular values
            value = [value]
        return [str(val) for val in value]

class Select2MultipleModelChoiceFilter(ModelMultipleChoiceFilter):
    field_class = Select2ModelMultipleChoiceField

    def to_python(self, value):
        """
        Overrides method to accomodate singular values instead of raising ValidationError
        """
        if not value:
            return []
        elif isinstance(value, str): # Singular values
            value = [value]
        return [str(val) for val in value]
