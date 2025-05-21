from datetime import datetime
import json
from json import JSONDecodeError
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django_filters.fields import RangeField
from django.utils.choices import CallableChoiceIterator

class CustomBooleanField(forms.BooleanField):
    """
    Converts the true/false string in the form data
    """
    def to_python(self, value):
        return True if value == 'true' else False

class CustomDateTimeField(forms.DateTimeField):
    """
    Converts between the Datetime object in the database
    and the formatted datetime string which is presented
    on webpages and forms and so forth.
    """
    # Convert the datetime-local string to a Python datetime object
    def to_python(self, value):
        if not value:
            return None
        return datetime.strptime(value, '%Y-%m-%dT%H:%M')

    # Convert the Python datetime object to a datetime-local string
    def prepare_value(self, value):
        if not value:
            return None
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        elif isinstance(value, datetime):
            pass
        value = value.strftime('%Y-%m-%dT%H:%M')
        return value

class CustomNumericRangeField(RangeField):
    def compress(self, data_list):
        if data_list:
            for index, item in enumerate(data_list):
                try:
                    data_list[index] = float(item)
                except TypeError:
                    pass # TODO, this is acceptable?
            return data_list
            # return slice(*data_list) # Overwritten, slice object not usable
        return None

class Select2ModelChoiceField(forms.ModelChoiceField):
    """
    forms.ModelChoiceField attempts to validate using the initial given queryset.
    As these querysets are too large to be included initially, preferring
    Select2 widget's Ajax functionality to request results from the API,
    the selected value is validated against all objects of this model.
    """
    def _get_queryset(self):
        return self._queryset

    def _set_queryset(self, queryset):
        self._queryset = None if queryset is None else queryset.all()
        self.widget.choices = self.choices

    def _get_choices(self):
        # If self._choices is set, then somebody must have manually set
        # the property self.choices. In this case, just return self._choices.
        if hasattr(self, '_choices'):
            return self._choices

        # Otherwise, execute the QuerySet in self.queryset to determine the
        # choices dynamically. Return a fresh ModelChoiceIterator that has not been
        # consumed. Note that we're instantiating a new ModelChoiceIterator *each*
        # time _get_choices() is called (and, thus, each time self.choices is
        # accessed) so that we can ensure the QuerySet has not been consumed. This
        # construct might look complicated but it allows for lazy evaluation of
        # the queryset.
        return self.iterator(self)

    def _set_choices(self, value):
        # Setting choices also sets the choices on the widget.
        # choices can be any iterable, but we call list() on it because
        # it will be consumed more than once.
        if callable(value):
            value = CallableChoiceIterator(value)
        else:
            value = list(value)
        self._choices = self.widget.choices = value

    choices = property(_get_choices, _set_choices)

    def prepare_value(self, value):
        if hasattr(value, '_meta'):
            if self.to_field_name:
                return value.serializable_value(self.to_field_name)
            else:
                return value.pk
        return super().prepare_value(value)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            if isinstance(value, self.queryset.model):
                value = getattr(value, key)
            # value = self.queryset.get(**{key: value}) # Original
            value = self.queryset.model.objects.get(**{key: value}) # validate using all objects of this model.
        except (ValueError, TypeError, self.queryset.model.DoesNotExist) as e:
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value

class Select2MultipleChoiceField(forms.MultipleChoiceField):
    def to_python(self, value):
        if not value:
            return []
        if not isinstance(value, list):
            return [value]
        return value

    def prepare_value(self, value):
        if not value:
            return []
        if isinstance(value, list):
            value = value[0]
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except JSONDecodeError: # Single values cause DecodeError
                pass
            if isinstance(value, int):
                value = [value]
            else:
                value = value.split(',')
        return value


class Select2ModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def to_python(self, value):
        if not value:
            return []
        if not isinstance(value, list):
            return [value]
        return value

    def prepare_value(self, value):
        if isinstance(value, str):
            value = value.split(',')
        if (hasattr(value, '__iter__') and
                not isinstance(value, str) and
                not hasattr(value, '_meta')):
            prepare_value = super().prepare_value
            return [prepare_value(v) for v in value]
        return super().prepare_value(value)

    def _check_values(self, value):
        """
        Given a list of possible PK values, return a QuerySet of the
        corresponding objects. Raise a ValidationError if a given value is
        invalid (not a valid PK, not in the queryset, etc.)
        """
        key = self.to_field_name or "pk"
        # deduplicate given values to avoid creating many querysets or
        # requiring the database backend deduplicate efficiently.
        try:
            value = frozenset(value)
        except TypeError:
            # list of lists isn't hashable, for example
            raise ValidationError(
                self.error_messages["invalid_list"],
                code="invalid_list",
            )
        for pk in value:
            try:
                # self.queryset.filter(**{key: pk}) # Original
                self.queryset.model.objects.filter(**{key: pk})
            except (ValueError, TypeError):
                raise ValidationError(
                    self.error_messages["invalid_pk_value"],
                    code="invalid_pk_value",
                    params={"pk": pk},
                )
        # qs = self.queryset.filter(**{"%s__in" % key: value}) # Original
        qs = self.queryset.model.objects.filter(**{f"{key}__in": value})
        pks = {str(getattr(o, key)) for o in qs}
        for val in value:
            if str(val) not in pks:
                raise ValidationError(
                    self.error_messages["invalid_choice"],
                    code="invalid_choice",
                    params={"value": val},
                )
        return qs

class MultipleEmailField(forms.MultipleChoiceField):
    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except JSONDecodeError: # Single values cause DecodeError
                pass
            value = value.split(',')
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(
                self.error_messages["invalid_list"], code="invalid_list"
            )
        return [str(val) for val in value]

    def valid_value(self, value):
        """
        Check to see if the provided value is a valid choice. Looks for the
        given value first in the choices and then validates it as an email in
        general, allowing external emails to be added
        """
        text_value = str(value)
        for k, v in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2 or text_value == str(k2):
                        return True
            else:
                if value == k or text_value == str(k):
                    return True
        try:
            validate_email(value)
            return True
        except ValidationError:
            pass
        return False
