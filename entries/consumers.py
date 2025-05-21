from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user_from_token(self, token_key):
        # Safely query the database for the user associated with the token
        try:
            token = Token.objects.select_related('user').get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return AnonymousUser() # Return AnonymousUser if token is invalid

    async def connect(self):
        # Extract token from query string
        query_string = self.scope['query_string'].decode()
        params = dict(p.split('=') for p in query_string.split('&') if '=' in p)
        token_key = params.get('token')

        self.user = await self.get_user_from_token(token_key)

        if self.user is None or isinstance(self.user, AnonymousUser):
            # Reject the connection if token is invalid or user not found
            print("WebSocket connection rejected: Invalid token or user not found.")
            await self.close()
        else:
            # User authenticated successfully
            print(f"WebSocket connection accepted for user: {self.user.email}")
            self.user_group_name = f'user_{self.user.slug}' # Unique group name per user

            # Join user-specific group
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name # Unique identifier for this specific connection
            )

            await self.accept() # Accept the WebSocket connection

            # Optionally send a welcome message
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': f'Notification channel connected for user {self.user.email}'
            }))

    async def disconnect(self, close_code):
        # Runs when the WebSocket closes
        if hasattr(self, 'user_group_name'):
            print(f"WebSocket disconnected for user: {getattr(self.user, 'email', 'Unknown')}")
            # Leave user-specific group
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    # Receive message from WebSocket (optional, if frontend needs to send data)
    async def receive(self, text_data):
        # You might not need this if only pushing *to* the client
        # text_data_json = json.loads(text_data)
        # message = text_data_json['message']
        # print(f"Received message via WebSocket: {message}")
        # Example: Echo message back (usually you'd process it)
        # await self.send(text_data=json.dumps({'echo': message}))
        pass # Ignore messages from client for now

    async def send_notification(self, event):
        if type(event) is not dict:
            raise TypeError(f"Unknown type for event: {type(event)}")
        if event['message_type'] not in ['success', 'info', 'warning', 'error']:
            raise ValueError(f"Unknown event type: {event['message_type']}")
        await self.send(text_data=json.dumps(event))