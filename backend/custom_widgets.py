from django_filters.widgets import BooleanWidget, RangeWidget
from django.forms.widgets import DateInput, Select, SelectMultiple

class BlankBooleanWidget(BooleanWidget):
    template_name = 'widget/blankboolean_widget.html'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = (("", "---"), (True, "Yes"), (False, "No"))

class NumericRangeWidget(RangeWidget):
    template_name = 'widget/numericrange_widget.html'
    suffixes = ['_gt', '_lt']
    def __init__(self, *args, **kwargs):
        super(NumericRangeWidget, self).__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        value = [
            widget.value_from_datadict(data, files, self.suffixed(name, suffix))
            for widget, suffix in zip(self.widgets, self.suffixes)
        ]
        return value

class DateWidget(DateInput):
    input_type = 'date'

class DateRangeWidget(RangeWidget):
    template_name = 'widget/date_range.html'
    suffixes = ['_gte', '_lte']
    def __init__(self, *args, **kwargs):
        super(DateRangeWidget, self).__init__(*args, **kwargs)
        widgets = [
            DateWidget(),
            DateWidget()
        ]

class Select2Widget(Select):
    template_name = 'select/model_select_widget.html'
    option_template_name = 'select/select_option.html'

    def format_value(self, value):
        """Return selected values as a list."""
        if value is None and self.allow_multiple_selected:
            return []
        if not isinstance(value, (tuple, list)):
            value = [value]
        return [str(v) if v is not None else "" for v in value]

    def value_from_datadict(self, data, files, name):
        getter = data.get
        if self.allow_multiple_selected:
            try:
                getter = data.getlist
            except AttributeError:
                pass
        return getter(name)

class Select2MultipleWidget(SelectMultiple):
    template_name = 'select/multiple_select_widget.html'
    option_template_name = 'select/select_option.html'