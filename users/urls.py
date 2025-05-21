from django.urls import path, re_path

from .views import (
    UserRegistration, UserLogin, CurrentUser, SendNotification, BookmarksList
    )

urlpatterns = [
    path('api/users/register/', UserRegistration.as_view(), name='register'),
    path('api/users/login/', UserLogin.as_view(), name='login'),
    re_path('api/users/me/', CurrentUser.as_view(), name="current user"),
    re_path('api/notify/(?P<slug>[\w\-]+)/', SendNotification.as_view(), name='api notify user'),
    re_path('api/users/(?P<slug>[\w\-]+)/bookmarks/', BookmarksList.as_view(), name="bookmarks"),
]