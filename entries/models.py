from django.db import models
from django.utils.text import slugify
from backend.base_models import PrimaryObjectModel
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

class Entry(PrimaryObjectModel):
    class Meta:
        abstract = False
        app_label = 'entries'
        db_table = 'Entries'
        verbose_name = 'entry'
        verbose_name_plural = 'entries'
        default_related_name = 'entries'
        ordering = ('title',)

    title = models.CharField(max_length=120)
    slug = models.CharField(max_length=120, primary_key=True)

    description = models.TextField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title = self.title.title()
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save()
