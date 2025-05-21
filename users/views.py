import json
import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from backend.base_views import BaseModelAPI
from .models import BaseUser
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer


class UserRegistration(generics.CreateAPIView):
    queryset = BaseUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

class UserLogin(APIView):
    """
    API endpoint for user login.
    Accepts POST requests with 'email' and 'password'.
    Returns an auth token on successful login.
    """
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True) # Validate request data

        user = serializer.validated_data['user']
        # Generate or retrieve the token for the user
        token, created = Token.objects.get_or_create(user=user)

        # Optional: Log the user in for the Django session (useful if using browsable API)
        # login(request, user)
        return Response({
            'token': token.key,
            'email': user.email,
            'slug': user.slug
        }, status=status.HTTP_200_OK)

class CurrentUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SendNotification(APIView):
    """
    (Admin/Test) Endpoint to send a push notification to a specific user via WebSocket.
    Requires user ID in the URL.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, *args, **kwargs):
        try:
            user = BaseUser.objects.get(slug=slug)
        except user.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        channel_layer = get_channel_layer()
        user_group_name = f'user_{slug}'

        message_content = request.data.get('message', f'Test notification from server at {datetime.datetime.now()}')

        print(f"Attempting to send notification to group: {user_group_name}")

        # Send message to user group
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'send_notification', # Must match the handler method in the consumer
                'message_type': 'info',
                'message': message_content,
            }
        )

        return Response({"status": f"Notification sent attempt to group {user_group_name}"}, status=status.HTTP_200_OK)

class BookmarksList(BaseModelAPI):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = user.bookmarks.all()
        bookmarks = [{'entry': bookmark.entry.title, 'slug': bookmark.entry.slug} for bookmark in queryset]
        return Response(json.dumps(bookmarks), status=status.HTTP_200_OK)