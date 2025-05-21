import json
from django.db import models
from colorfield.fields import ColorField
from django.core.validators import URLValidator, EmailValidator


class ColourMixin(models.Model):
    """
    Adds a colour field to the model
    """
    class Meta:
        abstract = True

    colour = ColorField(default='#04245c')


class ContactMixin(models.Model):
    """
    Adds some standard contact information fields to the model.
    """
    class Meta:
        abstract = True

    # Contact Information
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="Phone Number")
    email_address = models.EmailField(verbose_name="Email Address", validators=[EmailValidator], null=True, blank=True)
    website = models.URLField(verbose_name="Website", validators=[URLValidator], null=True, blank=True)


class InfoFieldMixin(models.Model):
    """
    A simple mixin that adds a JSONfield for variable information
    which shall be loaded as attributes when the object is initialised.
    Should be used in conjunction with the InfoFieldModel to provide consistent
    structure.
    """
    class Meta:
        abstract = True

    infofields = models.JSONField(max_length=10000, verbose_name="InfoFields", null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            infofields = json.loads(self.infofields)
            try:
                for key, value in infofields.items():
                    setattr(self, key, value)
            except TypeError:  # infofields may be none
                pass
        except:
            pass

