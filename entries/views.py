import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Q
from django.utils.text import slugify
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from backend.base_views import BaseModelAPI, BaseModelFormView
from .openai_requests import request_new_entry
from .serializers import FullEntrySerializer, CreateEntrySerializer
from .models import Entry
from .tasks import hyperlink_entry

import logging
logger = logging.getLogger("django")

class EntryBase:
    model = Entry
    serializer_class = FullEntrySerializer

class CreateEntry(EntryBase, BaseModelAPI):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CreateEntrySerializer
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
class ViewEntry(EntryBase, BaseModelAPI):
    pass

class UpdateEntry(EntryBase, BaseModelFormView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

class RequestNewEntry(EntryBase, BaseModelAPI):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1) Immediately acknowledge
        response = Response(status=status.HTTP_202_ACCEPTED)
        # But continue processing on this same thread
        self._handle_request(request)
        return response

    def _handle_request(self, request):
        self.querydict = self.get_querydict()
        query = self.querydict['query'].lower()
        # Websocket connection
        channel_layer = get_channel_layer()
        group_name = f"user_{request.user.slug}"

        def notify(type_, message, **extra):
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "message_type": type_,
                    "message": message,
                    **extra
                }
            )

        if not query:
            notify("error", "Missing query parameter")
        elif len(query) > 50:
            notify("error", "This query is too long")
        else:
            try:
                entry = Entry.objects.get(slug=slugify(query))
                if entry:
                    notify("success", "Entry already exists", linkUrl=f"/entries/{slugify(query)}", linkLabel="View")
            except Entry.DoesNotExist:
                pass

        response = request_new_entry(query)
        with open(f"entries/files/{query}.txt", "w") as f:
            f.write(response)

        entry_data = {
            "title": query,
            "description": response,
            "created_by": request.user.email,
            "updated_by": request.user.email
        }
        serializer = CreateEntrySerializer(data=entry_data)
        if serializer.is_valid():
            serializer.save()
            notify("success", f"Entry for {query} created successfully", linkUrl=f"/entries/{serializer.instance.slug}", linkLabel="View")
            hyperlink_entry.delay(serializer.instance.pk)
        else:
            logger.error(f"{serializer.__class__.__name__} ERRORS: {serializer.errors}")
            notify("error", "Something went wrong")

class EntryList(EntryBase, BaseModelAPI):
    """
    List all entries.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self, 'querydict'):
            self.get_querydict()
        if self.querydict:
            if 'q' in self.querydict:
                query = self.querydict.pop('q')
                queryset = self.model.objects.filter(
                    Q(description__icontains=query) | Q(title__icontains=query)
                )
            queryset = self.model.objects.filter(**self.querydict)
        else:
            queryset = self.model.objects.all()
        return queryset

    def get(self, request):
        queryset = self.get_queryset()
        entries = [{'title': entry.title, 'slug': entry.slug} for entry in queryset]
        entries = json.dumps(entries)
        request.session['entries'] = entries
        return Response(entries, status=status.HTTP_200_OK)
        # if 'entries' not in request.session:
        #     entries = list(self.get_queryset().values('title', 'slug')[:50])    
        #     request.session['entries'] = entries
        #     return Response(entries, status=status.HTTP_200_OK)
        # else:
        #     return Response(request.session['entries'], status=status.HTTP_200_OK)