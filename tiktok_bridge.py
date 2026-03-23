import logging
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, DisconnectEvent, CommentEvent, GiftEvent
import data_state

logging.getLogger("TikTokLive").setLevel(logging.CRITICAL)

def _get_gift_lists():
    """Parse danh sách gift từ string phân tách dấu phẩy."""
    gifts_a = [g.strip().lower() for g in data_state.team_a_gift.split(",") if g.strip()]
    gifts_b = [g.strip().lower() for g in data_state.team_b_gift.split(",") if g.strip()]
    return gifts_a, gifts_b

def start_tiktok_thread(user_id):
    client = TikTokLiveClient(unique_id=f"@{user_id}")

    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        data_state.is_connected = True
        data_state.last_event = f"Da ket noi @{user_id}"

    @client.on(DisconnectEvent)
    async def on_disconnect(event: DisconnectEvent):
        data_state.is_connected = False
        data_state.last_event = "Mat ket noi"

    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        try:
            text = event.comment.strip()
            if text == data_state.team_a_comment:
                data_state.score_a += 1
                data_state.split_x = max(50, min(850, data_state.split_x + data_state.power_comment))
                data_state.shake_intensity = 3.0
                data_state.last_event = f"{event.user.nickname} -> DOI DO"
            elif text == data_state.team_b_comment:
                data_state.score_b += 1
                data_state.split_x = max(50, min(850, data_state.split_x - data_state.power_comment))
                data_state.shake_intensity = 3.0
                data_state.last_event = f"{event.user.nickname} -> DOI XANH"
        except Exception:
            pass

    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent):
        try:
            gift = event.gift

            # Lấy tên quà
            gift_name = ""
            try:    gift_name = gift.info.name
            except:
                try: gift_name = gift.name
                except: pass
            if not gift_name:
                return

            # Lấy số lượng
            count = 1
            try:    count = int(gift.count) or 1
            except:
                try: count = int(gift.repeat_count) or 1
                except: count = 1

            # Kiểm tra đang streak → bỏ qua
            try:
                if gift.streaking: return
            except AttributeError: pass
            try:
                if not gift.repeat_end: return
            except AttributeError: pass
            try:
                if not gift.end_flag: return
            except AttributeError: pass

            push = count * data_state.power_gift
            gift_name_lower = gift_name.lower()

            # So sánh với danh sách gift (hỗ trợ nhiều gift mỗi đội)
            gifts_a, gifts_b = _get_gift_lists()

            matched_a = any(g in gift_name_lower for g in gifts_a)
            matched_b = any(g in gift_name_lower for g in gifts_b)

            if matched_a:
                data_state.split_x = max(50, min(850, data_state.split_x + push))
                data_state.shake_intensity = 6.0
                data_state.last_event = f"{event.user.nickname} tang {gift_name} x{count} -> DO"
            elif matched_b:
                data_state.split_x = max(50, min(850, data_state.split_x - push))
                data_state.shake_intensity = 6.0
                data_state.last_event = f"{event.user.nickname} tang {gift_name} x{count} -> XANH"
            else:
                # Gift không thuộc đội nào — vẫn hiện tên
                data_state.last_event = f"{event.user.nickname} tang {gift_name} x{count}"

        except Exception:
            pass

    try:
        client.run()
    except Exception as e:
        data_state.last_event = f"Loi: {e}"
        data_state.is_connected = False