from django.urls import path, re_path
from .views import CreateEntry, ViewEntry, EntryList, RequestNewEntry

urlpatterns = [
    # path('entries/', EntryList.as_view(), name='entries'),
    # re_path('entries/(?P<slug>[\w\-]+)/$', ViewEntry.as_view(), name='view entry'),
]

api_urlpatterns = [
    path('api/entries/', EntryList.as_view(), name='api entries'),
    path('api/entries/create/', CreateEntry.as_view(), name='api create entry'),
    path('api/entries/request-new/', RequestNewEntry.as_view(), name='api entries request-new'),
    re_path('api/entries/(?P<slug>[\w\-]+)/$', ViewEntry.as_view(), name='api view entry'),
]

urlpatterns += api_urlpatterns
