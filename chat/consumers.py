import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
   
    '''
    Adds the user that connected to the room to
    a channel where other participants of the room are 
    '''
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        print("connect()")
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    '''
    Removes the user from the channel 
    '''
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    '''
    Receives either an event or message and performs commands 
    '''
    async def receive(self, text_data):
        jsonData = json.loads(text_data)
        eventData = jsonData.get("event")
        if eventData:
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_event", "event": eventData}
            )
        else:
            messageData = jsonData.get("message")
            new_message = await database_sync_to_async(self.create_message)(
                messageData["user"], messageData["roomId"], messageData["text"]
            )
            messageData["id"] = new_message.id
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message": messageData}
            )
    '''
    Sends the message to the websocket  
    '''
    async def chat_message(self, event):
        messageData = event["message"]
        await self.send(text_data=json.dumps({"message": messageData}))
    
    '''
    Sends the event to the websocket  
    '''
    async def chat_event(self, event):  
        eventData = event["event"]
        await self.send(text_data=json.dumps({"event": eventData}))

    '''
    Saves the message in database  
    '''
    def create_message(self, user_id, room_id, text):
        created_message = Message.objects.create(
            room_id=room_id, user_id=user_id, text=text
        )
        return created_message
