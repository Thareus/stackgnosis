from django.db import models
from django.utils.text import slugify
from backend.base_models import PrimaryObjectModel, SecondaryObjectModel
from colorfield.fields import ColorField

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


class TagManager(models.Manager):
    def get_or_create(self, **kwargs):
        if 'name' not in kwargs:
            raise KeyError(f'get_or_create method is dependent on a tag name, not {kwargs}')
        try:
            return Tag.objects.get(name=kwargs['name'])
        except Tag.DoesNotExist:
            tag = Tag(**kwargs)
            tag.save()
        return tag

class Tag(SecondaryObjectModel):
    class Meta:
        app_label = 'tags'
        db_table = 'Tag'
        verbose_name = 'tag'
        default_related_name = 'tags'
        verbose_name_plural = 'tags'
        ordering = ['slug']
        indexes = [
            models.Index(fields=['name', ]),
        ]
        abstract = False

    name = models.CharField(max_length=50, null=False, blank=False)
    colour = ColorField(default='#FFF')
    hidden = models.BooleanField(default=False, verbose_name='Hidden', null=False, blank=False)
    # Slug
    slug = models.SlugField(primary_key=True)

    objects = TagManager()

    def __str__(self):
        return self.name

    @property
    def taggeditems_count(self):
        if not hasattr(self, '_taggeditems_count'): # TODO cache
            self._taggeditems_count = self.taggeditems.all().count()
        return self._taggeditems_count

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:100]
        super(Tag, self).save(*args, **kwargs)

class TaggedItemManager(models.Manager):
    def get_or_create(self, **kwargs):
        try:
            get_kwargs = ['tag', 'model', 'instance_slug']
            return TaggedItem.objects.get(**{get_kwarg:kwargs[get_kwarg] for get_kwarg in get_kwargs})
        except TaggedItem.DoesNotExist:
            taggeditem = TaggedItem(**kwargs)
            taggeditem.save()
        return taggeditem

class TaggedItem(SecondaryObjectModel):
    class Meta(SecondaryObjectModel.Meta):
        app_label = 'tags'
        db_table = 'TaggedItem'
        verbose_name = "tagged item"
        verbose_name_plural = "tagged items"
        default_related_name = 'taggeditems'
        ordering = ['tag']
        unique_together = (('tag', 'model', 'instance_slug'),)
        abstract = False

    tag = models.ForeignKey(Tag, verbose_name="tag", on_delete=models.CASCADE, related_name='taggeditems', related_query_name='taggeditem')
    tagged_by = models.ForeignKey("users.BaseUser", editable=True, null=False, blank=False, on_delete=models.DO_NOTHING, related_name='taggeditems', related_query_name='taggeditem')
    objects = TaggedItemManager()

    def __str__(self):
        return f"{self.tag} - {self.instance_slug}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.tag} {self.instance_slug}")[:200]
        super().save(*args, **kwargs)

class Bookmark(PrimaryObjectModel):
    class Meta:
        app_label = 'tags'
        db_table = 'Bookmark'
        verbose_name = 'bookmark'
        default_related_name = 'bookmarks'
        verbose_name_plural = 'bookmarks'
        abstract = False

    user = models.ForeignKey("users.BaseUser", editable=True, null=False, blank=False, on_delete=models.DO_NOTHING, related_name='bookmarks', related_query_name='bookmark')
    entry = models.ForeignKey("entries.Entry", editable=True, null=False, blank=False, on_delete=models.DO_NOTHING, related_name='bookmarked', related_query_name='bookmarked')