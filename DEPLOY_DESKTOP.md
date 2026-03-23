# Deploy Desktop App (Windows)

## 1) Chuẩn bị môi trường

1. Cài Python 3.11+.
2. Đứng tại thư mục project.
3. Cài dependencies:

```powershell
python -m pip install -r requirements.txt
```

## 2) Build file .exe

Chạy script build:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_desktop.ps1 -Clean
```

Kết quả nằm ở:

```text
dist/PUSH-BATTLE.exe
```

## 3) Chạy bản đóng gói

```powershell
dist/PUSH-BATTLE.exe
```

## 4) Checklist trước khi phát hành

1. Mở app và test từng màn: Menu, Connect, Settings, Game.
2. Test resize/maximize và kiểm tra bố cục không lệch.
3. Test input hotkey: Ctrl+V, Ctrl+C, Ctrl+X, Ctrl+A, giữ Backspace.
4. Test kết nối TikTok ID thật và xử lý mất kết nối.
5. Kiểm tra chạy được file `dist/PUSH-BATTLE.exe` trên máy test.

## 5) Lưu ý bảo mật

1. Không commit .env, token, hoặc session key.
2. Không commit dist/ và build/.
3. Chỉ commit mã nguồn + cấu hình mẫu (.env.example).
