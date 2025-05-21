from django import forms
from typing import Optional, Dict, Any, Union

from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

class FormErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''
        return mark_safe(''.join(
            [': %s' % e for e in self]
        ))

class BaseForm(forms.Form):
    """
    An enhanced Form class that adds useful features for better UX and developer experience.
    """
    class Meta:
        error_class = FormErrorList

    def __init__(self, *args, **kwargs):
        # Extract custom attributes before calling parent's __init__
        self.form_description = kwargs.pop('form_description', '')
        self.section_descriptions = kwargs.pop('section_descriptions', {})
        self.help_position = kwargs.pop('help_position', 'below')  # 'below' or 'aside'
        self.request = kwargs.pop('request', None)
        # Initialize any other custom attributes
        self.success_message: Optional[str] = None
        self._sections: Dict[str, str] = {}
        if 'sections' in kwargs:
            for section in kwargs.pop('sections', ''):
                self.add_section(*section)

        # Apply initial values with advanced configuration options
        initial_values = kwargs.pop('initial_values', {})

        super().__init__(*args, **kwargs)

        for field_name, value in initial_values.items():
            if field_name in self.fields:
                self._set_initial_value(field_name, value)

    def get_form_description(self) -> str:
        """Returns a formatted description of the form's purpose."""
        if self.form_description:
            return mark_safe(f'<div class="form-description">{self.form_description}</div>')
        return ''

    def get_initial_values(self) -> Dict[str, Any]:
        """
        Retrieve current initial values for all fields.
        """
        return {name: field.initial for name, field in self.fields.items() if field.initial is not None}

    def set_field_initial(self, field_name: str, value: Union[Any, Dict[str, Any]]) -> None:
        """
        Public method to set or update initial values after form initialization.
        """
        self._set_initial_value(field_name, value)

    def _set_initial_value(self, field_name: str, value: Union[Any, Dict[str, Any]]) -> None:
        """
        Set initial values with advanced configuration.

        Supports:
        - Simple values
        - Callable values
        - Conditional initial values
        - Value transformations
        """
        if isinstance(value, dict):
            # Advanced configuration for initial value
            config = value
            initial_value = config.get('value')

            # Optional transformer function
            transformer = config.get('transformer')
            if transformer and callable(transformer):
                initial_value = transformer(initial_value)

            # Optional condition
            condition = config.get('condition')
            if condition is None or (callable(condition) and condition()):
                self.fields[field_name].initial = initial_value
        else:
            # Simple initial value
            self.fields[field_name].initial = value

    def add_section(self, section_name: str,  fields: list, description: str = '') -> None:
        """
        Group fields into logical sections with optional descriptions.
        Useful for long forms that need organization.
        # Example:
        def __init__(self, *args, **kwargs):
            self.add_section(
                ['username', 'email'],
                'Account Details',
                'Basic information for your account'
            )
        """
        for field in fields:
            self._sections[field] = section_name
        if description:
            self.section_descriptions[section_name] = description

    def get_section_fields(self, section_name: str) -> list:
        """Get all fields belonging to a specific section."""
        return [field for field, section in self._sections.items() if section == section_name]


    def add_dynamic_field(self, field_name: str, field_type: forms.Field, **kwargs) -> None:
        """Dynamically add a new field to the form."""
        self.fields[field_name] = field_type(**kwargs)


    def get_field_help_text_position(self, field_name: str) -> str:
        """
        Allow per-field customization of help text position.
        Defaults to form-level setting.
        """
        return getattr(self.fields[field_name], 'help_position', self.help_position)

    def clean(self) -> Dict[str, Any]:
        """
        Enhanced clean method that supports cross-field validation
        and setting success messages.
        """
        cleaned_data = super().clean()
        self.cross_field_validation(cleaned_data)
        return cleaned_data

    def cross_field_validation(self, cleaned_data: Dict[str, Any]) -> None:
        """
        Override this method to implement custom cross-field validation logic.
        Raises ValidationError if validation fails.
        """
        pass

    def set_success_message(self, message: str) -> None:
        """Set a success message to be displayed after successful form submission."""
        self.success_message = message

class BaseModelForm(BaseForm, forms.ModelForm):
    class Meta:
        model = None
        exclude = [
            'date_created',
            'date_updated'
        ]

class CSVUploadForm(forms.Form):
    file = forms.FileField(
        label='',
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'hidden',  # Hide the actual file input
            'accept': '.csv'    # Only accept CSV files
        })
    )

class ImageUploadForm(forms.Form):
    image = forms.ImageField()