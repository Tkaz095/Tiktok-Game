import pygame
import sys
import math
import random
import threading
import data_state
from tiktok_bridge import start_tiktok_thread

# --- 1. KHỞI TẠO ---
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Push Battle TikTok Live - Pro Edition")
clock = pygame.time.Clock()

def get_font(size, bold=False):
    for f in ["segoeui", "arial", "tahoma"]:
        try: return pygame.font.SysFont(f, size, bold=bold)
        except: continue
    return pygame.font.Font(None, size)

# --- 2. HỆ THỐNG HẠT (PARTICLE SYSTEM - GIỮ NGUYÊN) ---
particles = []

def spawn_particles(x, y, color, count=12):
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 7)
        particles.append({
            "x": x, "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(30, 60),
            "max_life": 60,
            "color": color,
            "radius": random.randint(3, 7)
        })

def update_draw_particles(surf):
    dead = []
    for p in particles:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.15
        p["life"] -= 1
        if p["life"] <= 0:
            dead.append(p)
            continue
        alpha = int(255 * p["life"] / p["max_life"])
        r = max(1, int(p["radius"] * p["life"] / p["max_life"]))
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*p["color"], alpha), (r, r), r)
        surf.blit(s, (int(p["x"])-r, int(p["y"])-r))
    for p in dead: particles.remove(p)

# --- 3. CÁC CLASS UI (BUTTON, INPUTBOX - GIỮ NGUYÊN) ---
class Button:
    def __init__(self, x, y, w, h, text, color, border=None, font=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.border = border
        self.font = font
        self.hover = False

    def draw(self, surf):
        c = [min(v + 35, 255) for v in self.color] if self.hover else self.color
        if self.border:
            pygame.draw.rect(surf, (30,30,45), self.rect, border_radius=10)
            pygame.draw.rect(surf, self.border if not self.hover else (255,255,255), self.rect, 2, border_radius=10)
        else:
            pygame.draw.rect(surf, c, self.rect, border_radius=10)
        t = self.font.render(self.text, True, (255,255,255))
        surf.blit(t, t.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION: self.hover = self.rect.collidepoint(event.pos)
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover

class InputBox:
    def __init__(self, x, y, w, h, font, text="", numeric=False, hint=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = str(text)
        self.numeric = numeric
        self.active = False
        self.font = font
        self.hint = hint

    def draw(self, surf):
        pygame.draw.rect(surf, (20, 20, 30), self.rect, border_radius=5)
        pygame.draw.rect(surf, (255, 46, 99) if self.active else (120, 120, 130), self.rect, 2, border_radius=5)
        txt = self.text if (self.text or self.active) else self.hint
        color = (255,255,255) if (self.text or self.active) else (100, 100, 100)
        t_surf = self.font.render(txt + ("|" if self.active else ""), True, color)
        surf.blit(t_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - t_surf.get_height()) // 2))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN: self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
            elif not self.numeric or event.unicode.isnumeric() or event.unicode in ".-": self.text += event.unicode

# --- 4. HÀM VẼ HỖ TRỢ (DRAW HELPERS) ---

def draw_hud(surf, font, font_small):
    hud_h = 44
    s = pygame.Surface((WIDTH, hud_h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 160))
    surf.blit(s, (0, 0))
    dot_color = (46, 204, 113) if data_state.is_connected else (180, 60, 60)
    pygame.draw.circle(surf, dot_color, (16, hud_h // 2), 7)
    t = font.render(f"LIVE: @{data_state.tiktok_id}" if data_state.is_connected else "CHỜ KẾT NỐI...", True, (255,255,255))
    surf.blit(t, (30, hud_h // 2 - t.get_height() // 2))
    ev = font_small.render(data_state.last_event, True, (255, 220, 0))
    surf.blit(ev, (WIDTH - ev.get_width() - 10, hud_h // 2 - ev.get_height() // 2))

def draw_ultra_divider(surf, split_x, shake, font):
    sx = int(split_x + random.uniform(-shake, shake))
    # Hiệu ứng Neon Glow cho Divider
    for i in range(10, 0, -2):
        s = pygame.Surface((i*2, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 50//i), (0, 0, i*2, HEIGHT))
        surf.blit(s, (sx - i, 0))
    pygame.draw.line(surf, (255,255,255), (sx, 0), (sx, HEIGHT), 3)
    cx, cy = sx, HEIGHT // 2
    pygame.draw.circle(surf, (255,255,255), (cx, cy), 22)
    pygame.draw.circle(surf, (0,0,0), (cx, cy), 18)
    t = font.render("⚔", True, (255,255,255))
    surf.blit(t, t.get_rect(center=(cx, cy)))

def draw_score_bar(surf, split_x, font):
    bar_h = 28
    bar_y = HEIGHT - bar_h
    total = max(data_state.score_a + data_state.score_b, 1)
    ratio_a = data_state.score_a / total
    pygame.draw.rect(surf, (20, 20, 30), (0, bar_y, WIDTH, bar_h))
    pygame.draw.rect(surf, (220, 60, 60), (0, bar_y, int(WIDTH * ratio_a), bar_h))
    pygame.draw.rect(surf, (60, 100, 220), (int(WIDTH * ratio_a), bar_y, WIDTH, bar_h))
    sa = font.render(str(data_state.score_a), True, (255,255,255))
    sb = font.render(str(data_state.score_b), True, (255,255,255))
    surf.blit(sa, (10, bar_y + 2))
    surf.blit(sb, (WIDTH - sb.get_width() - 10, bar_y + 2))

# --- 5. HÀM MAIN (HỢP NHẤT LOGIC) ---
def main():
    # Fonts khởi tạo trong main
    font_title = get_font(50, True)
    font_menu = get_font(24, True)
    font_text = get_font(20)
    font_small = get_font(16)
    font_big = get_font(72, True)

    # UI Objects
    btn_start = Button(WIDTH//2-150, 350, 300, 50, "BẮT ĐẦU LIVE", (255, 46, 99), font=font_menu)
    btn_test = Button(WIDTH//2-150, 420, 300, 50, "CHẾ ĐỘ TEST", (50, 50, 70), border=(255, 220, 0), font=font_menu)
    btn_set = Button(WIDTH//2-150, 490, 300, 50, "CÀI ĐẶT", (50, 50, 70), border=(8, 217, 214), font=font_menu)
    btn_save = Button(WIDTH//2-150, 530, 300, 45, "LƯU CÀI ĐẶT", (46, 204, 113), font=font_menu)
    btn_back = Button(20, HEIGHT-60, 150, 40, "<- QUAY LẠI", (30,30,45), border=(255,255,255), font=font_menu)

    id_box = InputBox(WIDTH//2-200, HEIGHT//2-25, 400, 50, font_text, hint="Nhập ID TikTok...")
    
    settings_boxes = {
        "p_com":  InputBox(450, 210, 400, 35, font_text, text="3.0", numeric=True),
        "p_gift": InputBox(450, 255, 400, 35, font_text, text="15.0", numeric=True),
        "gift_a": InputBox(450, 345, 400, 35, font_text, text="Rose"),
        "gift_b": InputBox(450, 390, 400, 35, font_text, text="Ice Cream"),
    }

    try:
        r_org = pygame.image.load("assets/man.png").convert_alpha()
        b_org = pygame.image.load("assets/woman.png").convert_alpha()
        b_org = pygame.transform.flip(b_org, True, False)
        imgs_ok = True
    except: imgs_ok = False

    state = "MENU"
    smooth_split_x = 450.0  # Hiệu ứng mượt (Lerp)
    prev_split_x = 450.0

    while True:
        screen.fill((15, 15, 25))
        dt = clock.tick(60)

        # Logic mượt
        if data_state.shake_intensity > 0: data_state.shake_intensity -= 0.2
        smooth_split_x += (data_state.split_x - smooth_split_x) * 0.1 # Đây là logic đẩy mượt

        # Hạt hiệu ứng khi có lực đẩy
        if abs(data_state.split_x - prev_split_x) > 5:
            color = (220, 60, 60) if data_state.split_x > prev_split_x else (60, 100, 220)
            spawn_particles(int(smooth_split_x), HEIGHT//2, color)
        prev_split_x = data_state.split_x

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            if state == "MENU":
                if btn_start.handle(event): state = "CONNECT"
                if btn_test.handle(event): state = "GAME"
                if btn_set.handle(event): state = "SETTINGS"
            elif state == "CONNECT":
                id_box.handle(event)
                if btn_back.handle(event): state = "MENU"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    uid = id_box.text.strip()
                    if uid:
                        data_state.tiktok_id = uid
                        threading.Thread(target=start_tiktok_thread, args=(uid,), daemon=True).start()
                        state = "GAME"
            elif state == "SETTINGS":
                for box in settings_boxes.values(): box.handle(event)
                if btn_save.handle(event):
                    data_state.power_comment = float(settings_boxes["p_com"].text)
                    data_state.power_gift = float(settings_boxes["p_gift"].text)
                    data_state.team_a_gift = settings_boxes["gift_a"].text
                    data_state.team_b_gift = settings_boxes["gift_b"].text
                    state = "MENU"
                if btn_back.handle(event): state = "MENU"
            elif state == "GAME":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: state = "MENU"
                    if event.key == pygame.K_1: 
                        data_state.split_x += 20
                        data_state.score_a += 1
                        data_state.shake_intensity = 5
                    if event.key == pygame.K_2: 
                        data_state.split_x -= 20
                        data_state.score_b += 1
                        data_state.shake_intensity = 5

        # VẼ GIAO DIỆN THEO STATE
        if state == "MENU":
            t = font_title.render("⚔ PUSH BATTLE", True, (255, 46, 99))
            screen.blit(t, (WIDTH//2 - t.get_width()//2, 150))
            btn_start.draw(screen); btn_test.draw(screen); btn_set.draw(screen)
        
        elif state == "CONNECT":
            screen.blit(font_menu.render("NHẬP ID TIKTOK VÀ NHẤN ENTER", True, (8, 217, 214)), (WIDTH//2-185, HEIGHT//2-80))
            id_box.draw(screen); btn_back.draw(screen)
            
        elif state == "SETTINGS":
            screen.blit(font_title.render("⚙ CÀI ĐẶT", True, (255,255,255)), (20, 20))
            labels = ["Lực Comment", "Lực Quà", "Quà Đỏ", "Quà Xanh"]
            for i, label in enumerate(labels):
                screen.blit(font_text.render(label, True, (255,255,255)), (150, 210 + i*45))
            for i, box in enumerate(settings_boxes.values()): box.draw(screen)
            btn_save.draw(screen); btn_back.draw(screen)

        elif state == "GAME":
            # Vẽ nền động
            pygame.draw.rect(screen, (40, 10, 10), (0, 0, int(smooth_split_x), HEIGHT))
            pygame.draw.rect(screen, (10, 10, 40), (int(smooth_split_x), 0, WIDTH, HEIGHT))
            
            if imgs_ok:
                rf = max(1.0, 1.0 + (smooth_split_x - 450)/450 * 0.7)
                bf = max(1.0, 1.0 + (450 - smooth_split_x)/450 * 0.7)
                ri = pygame.transform.smoothscale(r_org, (int(280*rf), int(280*rf)))
                bi = pygame.transform.smoothscale(b_org, (int(280*bf), int(280*bf)))
                screen.blit(ri, (smooth_split_x/2 - ri.get_width()/2, HEIGHT//2 - ri.get_height()/2))
                screen.blit(bi, (smooth_split_x + (WIDTH-smooth_split_x)/2 - bi.get_width()/2, HEIGHT//2 - bi.get_height()/2))
            
            update_draw_particles(screen)
            draw_ultra_divider(screen, smooth_split_x, data_state.shake_intensity, font_menu)
            draw_score_bar(screen, smooth_split_x, font_menu)
            draw_hud(screen, font_menu, font_small)
            # Nhãn đội
            screen.blit(font_menu.render("ĐỘI ĐỎ", True, (255,255,255)), (smooth_split_x // 2 - 40, HEIGHT - 70))
            screen.blit(font_menu.render("ĐỘI XANH", True, (255,255,255)), (smooth_split_x + (WIDTH-smooth_split_x)//2 - 40, HEIGHT - 70))

        pygame.display.flip()

if __name__ == "__main__":
    main()