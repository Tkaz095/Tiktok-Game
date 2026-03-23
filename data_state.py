import threading
_lock = threading.Lock()

split_x = 450.0
score_a = 0
score_b = 0
shake_intensity = 0.0
last_event = ""
last_user = ""
tiktok_id = ""
is_connected = False
power_comment = 3.0
power_gift = 15.0

# Nhiều gift mỗi đội, phân tách bằng dấu phẩy
team_a_gift = "Rose,TikTok Universe,Lion,Doughnut"
team_b_gift = "Ice Cream,Sunglasses,Heart Me,GG"

team_a_comment = "1"
team_b_comment = "2"