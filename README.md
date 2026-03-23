# Tiktok-Game

Đây là tựa game tương tác (Push Battle) trên TikTok Live. Khán giả trên phiên live có thể bình luận hoặc tặng quà để tương tác tạo lực đẩy trong game.

## Công dụng của các file

- **`main.py`**: Chứa vòng lặp game chính, xử lý giao diện hiển thị đồ họa, hiệu ứng (Particle System) sử dụng thư viện `pygame`. Đây là file chạy (điểm truy cập) của game.
- **`tiktok_bridge.py`**: Cầu nối giao tiếp với nền tảng TikTok. Xử lý các sự kiện thời gian thực (real-time stream) từ TikTok Live như bình luận (Comment Event) và tặng quà (Gift Event) bằng thư viện `TikTokLive`.
- **`data_state.py`**: Lưu trữ các biến trạng thái toàn cục dùng chung giữa luồng đồ họa Pygame và luồng mạng TikTok Live (điểm số, lượng đẩy, thông báo sự kiện, trạng thái kết nối).
- **`settings.json`**: Tập tin lưu trữ các cài đặt cấu hình thông số của game (mệnh lệnh, sức mạnh đẩy, loại quà tặng tương ứng từ người xem...).
- **`assets/`**: Thư mục chứa các tài nguyên ảnh, âm thanh của game.

## Hướng dẫn cách chạy game

1. **Cài đặt thư viện (Dependencies):**
   Bạn cần cài đặt Python trên máy, sau đó mở Terminal/Command Prompt và cài đặt các thư viện cần thiết bằng lệnh:
   ```bash
   pip install pygame TikTokLive
   ```

2. **Chạy ứng dụng:**
   Khởi động game bằng cách chạy file `main.py`:
   ```bash
   python main.py
   ```

3. **Sử dụng:**
   Khi game hiện lên, trên giao diện sẽ có ô để bạn nhập `TikTok ID` (ví dụ ID của bạn đang livestream). Nhấn kết nối để hệ thống bắt đầu tự nhận diện bình luận và quà tặng từ phiên livestream đó.

## Build Desktop App (Windows)

### 1) Cài dependencies

```bash
python -m pip install -r requirements.txt
```

### 2) Build file thực thi (.exe)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_desktop.ps1 -Clean
```

Sau khi build xong, app nằm trong thư mục:

```text
dist/PUSH-BATTLE.exe
```

### 3) Chạy bản Desktop

```powershell
dist/PUSH-BATTLE.exe
```

### 4) Tài liệu phát hành

- Quy trình deploy chi tiết: `DEPLOY_DESKTOP.md`
- Cấu hình đóng gói PyInstaller: `tiktok_game.spec`
- Danh sách dependency cố định version: `requirements.txt`
- Mẫu biến môi trường: `.env.example`
