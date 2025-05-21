from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

"""
Rules:
    - ForeignKey/ManytoMany fields must have the same name as the model, regardless of plurality.
        - This synchronises with the use of related_query_name, which defaults to the model name, meaning that 
          the model name, field name, and related_query_name will be consistent.
    - The default_related_name for all models must be the model verbose name plural without spaces.
        - This synchronises with the above rule. Such singular/plural name references are used in API logic.
        - Singular will always refer to the field/related_query_name, plural is reserved for objects of that field model.
        - Where default_related_name is relevant, there will not be a field.
    - All models should prefetch_related for related objects.
"""

class BaseModelManager(models.Manager):
    def get_readonly_fields(self, request, obj=None):
        defaults = super().get_readonly_fields(request, obj=obj)
        if obj:
            defaults = tuple(defaults) + ('label',)
        return defaults
    
class BaseModelMetaValidator(models.base.ModelBase):
    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        meta = getattr(new_class, '_meta', None)

        if meta and not meta.abstract:
            required_meta_fields = ['app_label', 'db_table', 'verbose_name', 'verbose_name_plural', 'default_related_name']
            for field in required_meta_fields:
                if not getattr(meta, field, None):
                    raise ValueError(f"Abstract model '{name}' must define '{field}' in its Meta class.")
        
        return new_class

class BaseModel(models.Model, metaclass=BaseModelMetaValidator):
    """
    Contains some basic information fields that are desirable for most models.
    """
    class Meta:
        abstract = True
        db_table = ""  # Must be defined
        verbose_name = ""  # Must be defined
        verbose_name_plural = ""  # Must be defined
        default_related_name = "" # Must be defined (verbose_name_plural.replace(" ", ""))

    # Slug
    slug = models.SlugField(max_length=200, editable=False, unique=True) # Not set to primary key to avoid composite primary keys
    # Date Created
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created", editable=False)
    created_by = models.ForeignKey("users.BaseUser", editable=True, null=False, blank=False, on_delete=models.DO_NOTHING,
                                    related_name="%(class)s_created_by")

    # Date Updated
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Date Updated", editable=False)
    updated_by = models.ForeignKey("users.BaseUser", editable=True, null=False, blank=False, on_delete=models.DO_NOTHING,
                                    related_name="%(class)s_updated_by")
    objects = BaseModelManager()

class PrimaryObjectModel(BaseModel):
    """
    Differs from the BaseModel mainly in the sense that it gathers all SecondaryObjectModels to it
    in the form of Generic Relations.

    Generic Relations are usually predicated on primary_keys which makes sense I suppose.
    There is the ability to change the object_id_field, but the GenericRelatedObjectManager
    intrinsically uses the primary key when constructing the filter used to get the related objects.
    object_id_field appears to be more for display.
    """
    class Meta:
        abstract = True
        db_table = ""  # Must be defined
        verbose_name = ""  # Must be defined
        verbose_name_plural = ""  # Must be defined
        default_related_name = ""  # Must be defined (verbose_name_plural.replace(" ", ""))

    @property
    def tag_list(self):
        if not hasattr(self, '_tag_list'):
            self._tag_list = set([taggeditem.tag.name for taggeditem in self.taggeditems.all()])
        return self._tag_list


class SecondaryObjectQuerysetMixin(object):
    pass

class SecondaryObjectModelManager(models.Manager):
    pass

class SecondaryObjectModel(BaseModel):
    """
    An abstract model that defines core attributes of SecondaryObjects, which are
    intended to be based upon a GenericForeignKey relationship with any model deriving from a PrimaryObjectModel.
    """
    class Meta:
        abstract = True
        db_table = ""  # Must be defined
        verbose_name = ""  # Must be defined
        verbose_name_plural = ""  # Must be defined
        default_related_name = ""  # Must be defined (verbose_name_plural.replace(" ", ""))
        unique_together = ("model", "instance_slug")
        indexes = [
            models.Index(fields=["model", "instance_slug"]),
        ]

    model = models.ForeignKey(ContentType, verbose_name="model", on_delete=models.CASCADE)
    instance_slug = models.CharField(max_length=200, verbose_name="instance slug")
    content_object = GenericForeignKey(ct_field='model', fk_field='instance_slug')

    # Slug
    slug = models.SlugField(max_length=200, primary_key=True, editable=False, unique=True)

    @property
    def content_object_instance(self):
        """
        Returns the object instance indicated by the model and instance_slug
        """
        if hasattr(self.model, '_content_object_instance'):
            self._content_object_instance = self.model.get_object_for_this_type(slug=self.instance_slug)
            return self._content_object_instance
        else:
            raise AttributeError(f"Model {self.model} has no attribute 'get_object_for_this_type,' it must be defined.")