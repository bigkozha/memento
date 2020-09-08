import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    
    tile_won  = []
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.items = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        await self.send(text_data=json.dumps({
            'items': self.items,
            'tile_won': ChatConsumer.tile_won,
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        tile_opened = []
        if 'tileOpened' in text_data_json:
            tile_opened = text_data_json['tileOpened']
        if 'tile_won' in text_data_json:
            ChatConsumer.tile_won.extend(text_data_json['tile_won'])
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'tile_opened': tile_opened,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        if 'tile_opened' in event:
            tile_opened = event['tile_opened']
        else:
            tile_opened = ''
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'tile_opened': tile_opened,
        }))