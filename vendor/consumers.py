# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

class MetricConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("metrics_group", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("metrics_group", self.channel_name)

    async def update_metric(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
