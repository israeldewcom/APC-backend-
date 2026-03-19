import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.sync.models import SyncState, SyncQueue

class SyncConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f"sync_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.send_sync_state()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')
        if msg_type == 'sync_request':
            await self.send_sync_data()
        elif msg_type == 'ack':
            token = data.get('token')
            await self.update_sync_token(token)

    async def send_sync_state(self):
        token = await self.get_sync_token()
        await self.send(text_data=json.dumps({
            'type': 'sync_state',
            'token': token
        }))

    async def send_sync_data(self):
        changes = await self.get_pending_changes()
        await self.send(text_data=json.dumps({
            'type': 'sync_data',
            'changes': changes
        }))

    @database_sync_to_async
    def get_sync_token(self):
        state, _ = SyncState.objects.get_or_create(user=self.user, device_id=self.device_id)
        return state.last_sync_token

    @database_sync_to_async
    def update_sync_token(self, token):
        SyncState.objects.update_or_create(
            user=self.user,
            device_id=self.device_id,
            defaults={'last_sync_token': token}
        )

    @database_sync_to_async
    def get_pending_changes(self):
        pending = SyncQueue.objects.filter(user=self.user, device_id=self.device_id, synced_at__isnull=True)
        return [
            {
                'id': str(item.id),
                'action': item.action,
                'model': item.model_name,
                'object_id': item.object_id,
                'data': item.data,
                'created_at': item.created_at.isoformat()
            }
            for item in pending
        ]
