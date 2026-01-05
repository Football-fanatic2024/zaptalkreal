import re
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer, AsyncWebsocketConsumer

# ============================
# Utility: Safe group names
# ============================
def safe_group_name(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', name)


# ============================
# CHAT CONSUMER (1-on-1 + groups)
# ============================
class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        # 1-on-1 chat
        if "username" in self.scope["url_route"]["kwargs"]:
            other_username = self.scope["url_route"]["kwargs"]["username"]

            # Deterministic room name
            self.room_group = (
                f"chat_{safe_group_name(min(user.username, other_username))}_"
                f"{safe_group_name(max(user.username, other_username))}"
            )

        # Group chat
        elif "group_id" in self.scope["url_route"]["kwargs"]:
            group_id = self.scope["url_route"]["kwargs"]["group_id"]
            self.room_group = f"group_{safe_group_name(str(group_id))}"

        else:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "room_group"):
            await self.channel_layer.group_discard(self.room_group, self.channel_name)

    # ⭐ THIS WAS MISSING — this is why messages didn’t work
    async def receive_json(self, content):
        """
        Handles incoming chat messages.
        Expected JSON:
        {
            "text": "...",
            "sender": "...",
            "timestamp": "..."
        }
        """

        text = content.get("text")
        sender = content.get("sender")
        timestamp = content.get("timestamp")

        if not text:
            return

        # Broadcast to everyone in the room
        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "chat_message",
                "text": text,
                "sender": sender,
                "timestamp": timestamp,
            }
        )

    async def chat_message(self, event):
        await self.send_json({
            "sender": event["sender"],
            "text": event["text"],
            "timestamp": event["timestamp"],
        })


# ============================
# CALL CONSUMER (WebRTC signaling)
# ============================
class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Each user gets their own signaling group:
        call_<username>
        """

        self.username = self.scope["user"].username
        self.room_group_name = f"call_{safe_group_name(self.username)}"

        print(f"[CALL] Connected: {self.username}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Incoming WebRTC signaling messages:
        - offer
        - answer
        - ice
        Forward them to the target user's call group.
        """
        data = json.loads(text_data)

        target = data.get("to")
        if not target:
            return

        target_group = f"call_{safe_group_name(target)}"

        await self.channel_layer.group_send(
            target_group,
            {
                "type": "call_signal",
                "data": data
            }
        )

    async def call_signal(self, event):
        await self.send(text_data=json.dumps(event["data"]))
