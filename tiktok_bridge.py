# tiktok_bridge.py
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent
import data_state
import asyncio

async def run_tiktok(user_id):
    client = TikTokLiveClient(unique_id=f"@{user_id}")

    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        text = event.comment.strip()
        if text == "1":
            data_state.score_a += 1
            data_state.split_x += data_state.power_comment
        elif text == "2":
            data_state.score_b += 1
            data_state.split_x -= data_state.power_comment

    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent):
        gift_name = event.gift.info.name
        count = event.gift.repeat_count
        push = count * data_state.power_gift
        
        data_state.last_event = f"{event.user.nickname} tặng {gift_name}"
        
        if data_state.team_a_gift in gift_name:
            data_state.split_x += push
            data_state.shake_intensity = 6.0
        elif data_state.team_b_gift in gift_name:
            data_state.split_x -= push
            data_state.shake_intensity = 6.0

    try:
        await client.start()
        data_state.is_connected = True
    except Exception as e:
        data_state.last_event = f"Lỗi: {e}"
        data_state.is_connected = False

def start_tiktok_thread(user_id):
    asyncio.run(run_tiktok(user_id))