from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.text import slugify

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

class CustomBaseUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, **fields):
        """
        Create and save a User with the given email and password.
        """
        # Verify email
        email = fields['email']
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        email = email.lower()
        fields['email'] = email
        user = self.model(
            **fields
        )
        user.set_password(fields['password'])
        user.save()
        return user

    def create_superuser(self, **fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        fields.setdefault('is_staff', True)
        fields.setdefault('is_superuser', True)
        return self.create_user(**fields)


class BaseUser(AbstractBaseUser, PermissionsMixin):
    """
    This is the User model that is stored in the relational database backend
    so that it may take advantage of all the authentication and security features
    that are built into Django / into the allauth package.
    """
    class Meta:
        managed = True
        swappable = 'AUTH_USER_MODEL'
        app_label = 'users'
        db_table = "base_user"
        verbose_name = "base user"
        verbose_name_plural = "base users"
        default_related_name = "base_users"

    date_joined = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(primary_key=True)

    username = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, editable=False, unique=True)
    USERNAME_FIELD = 'username'

    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomBaseUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        slug = slugify(self.username)
        if not self.slug or slug != self.slug:
            self.slug = slug
        return super().save(*args, **kwargs)
        