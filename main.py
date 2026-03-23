import pygame
import sys
import math
import random
import threading
import data_state
from tiktok_bridge import start_tiktok_thread

pygame.init()
WIDTH, HEIGHT = 960, 620
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PUSH BATTLE - TikTok Live")
clock = pygame.time.Clock()

# ─── COLORS ───────────────────────────────────────────────
C_BG        = (8,   8,  16)
C_RED       = (230,  50,  80)
C_RED_DIM   = (120,  25,  40)
C_BLUE      = ( 50, 110, 240)
C_BLUE_DIM  = ( 20,  45, 110)
C_WHITE     = (255, 255, 255)
C_GOLD      = (255, 210,  60)
C_CYAN      = ( 30, 220, 200)
C_GRAY      = (100, 100, 120)
C_PANEL     = ( 18,  18,  30)
C_BORDER    = ( 50,  50,  70)
C_GREEN     = ( 46, 204, 113)

# ─── FONT LOADER ──────────────────────────────────────────
def get_font(size, bold=False):
    for f in ["segoeui", "tahoma", "arial"]:
        try: return pygame.font.SysFont(f, size, bold=bold)
        except: continue
    return pygame.font.Font(None, size)

# ─── PARTICLES ────────────────────────────────────────────
particles = []

def spawn_particles(x, y, color, count=16):
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.5, 6.5)
        particles.append({
            "x": x, "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed - random.uniform(0, 2),
            "life": random.randint(35, 65),
            "max_life": 65,
            "color": color,
            "radius": random.randint(2, 6)
        })

def update_draw_particles(surf):
    dead = []
    for p in particles:
        p["x"] += p["vx"]; p["y"] += p["vy"]; p["vy"] += 0.12; p["life"] -= 1
        if p["life"] <= 0: dead.append(p); continue
        a = int(255 * p["life"] / p["max_life"])
        r = max(1, int(p["radius"] * p["life"] / p["max_life"]))
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*p["color"], a), (r, r), r)
        surf.blit(s, (int(p["x"])-r, int(p["y"])-r))
    for p in dead: particles.remove(p)

# ─── DRAW HELPERS ─────────────────────────────────────────
def draw_rect_alpha(surf, color_alpha, rect, radius=0):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, color_alpha, (0, 0, rect[2], rect[3]), border_radius=radius)
    surf.blit(s, (rect[0], rect[1]))

def draw_text_shadow(surf, text, font, color, x, y, shadow_offset=2):
    sh = font.render(text, True, (0, 0, 0))
    surf.blit(sh, (x + shadow_offset, y + shadow_offset))
    t = font.render(text, True, color)
    surf.blit(t, (x, y))

def draw_glow_circle(surf, color, center, radius, layers=6):
    for i in range(layers, 0, -1):
        a = int(60 / i)
        r_extra = i * 4
        s = pygame.Surface(((radius + r_extra)*2, (radius + r_extra)*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, a), (radius + r_extra, radius + r_extra), radius + r_extra)
        surf.blit(s, (center[0] - radius - r_extra, center[1] - radius - r_extra))
    pygame.draw.circle(surf, color, center, radius)

# ─── STARFIELD BACKGROUND ────────────────────────────────
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.3, 1.2)) for _ in range(120)]

def draw_stars(surf, t):
    for sx, sy, spd in stars:
        brightness = int(80 + 60 * math.sin(t * spd * 0.05 + sx))
        pygame.draw.circle(surf, (brightness, brightness, brightness+20), (sx, sy), 1)

# ─── ANIMATED TITLE ──────────────────────────────────────
def draw_animated_title(surf, font_big, font_sub, t):
    title = "⚔  PUSH  BATTLE"
    chars = list(title)
    total_w = sum(font_big.size(c)[0] for c in chars)
    x = WIDTH // 2 - total_w // 2
    y_base = 130
    for i, c in enumerate(chars):
        wave = math.sin(t * 0.04 + i * 0.35) * 6
        # Gradient color per char
        ratio = i / max(len(chars)-1, 1)
        r = int(C_RED[0] + (C_BLUE[0] - C_RED[0]) * ratio)
        g = int(C_RED[1] + (C_BLUE[1] - C_RED[1]) * ratio)
        b = int(C_RED[2] + (C_BLUE[2] - C_RED[2]) * ratio)
        ch = font_big.render(c, True, (r, g, b))
        sh = font_big.render(c, True, (0, 0, 0))
        surf.blit(sh, (x + 3, y_base + wave + 3))
        surf.blit(ch, (x, y_base + wave))
        x += font_big.size(c)[0]

    sub = "TIKTOK LIVE BATTLE GAME"
    st = font_sub.render(sub, True, C_CYAN)
    pulse = int(180 + 75 * math.sin(t * 0.06))
    st.set_alpha(pulse)
    surf.blit(st, (WIDTH // 2 - st.get_width() // 2, 195))

# ─── BUTTON CLASS ────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text, accent, font, icon=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.accent = accent
        self.font = font
        self.icon = icon
        self.hover = False
        self.press_t = 0

    def draw(self, surf, t=0):
        glow = self.hover or self.press_t > 0
        # Shadow
        draw_rect_alpha(surf, (0, 0, 0, 80), (self.rect.x+4, self.rect.y+4, self.rect.w, self.rect.h), radius=12)
        # BG
        bg = (28, 28, 44) if not glow else (38, 38, 58)
        pygame.draw.rect(surf, bg, self.rect, border_radius=12)
        # Accent border
        border_a = 255 if glow else 160
        bw = 2 if not glow else 3
        s = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.accent, border_a), (0,0,self.rect.w,self.rect.h), bw, border_radius=12)
        surf.blit(s, self.rect.topleft)
        # Inner glow on hover
        if glow:
            draw_rect_alpha(surf, (*self.accent, 25), self.rect, radius=12)
        # Text
        label = f"{self.icon}  {self.text}" if self.icon else self.text
        tc = C_WHITE if glow else (210, 210, 220)
        txt = self.font.render(label, True, tc)
        surf.blit(txt, txt.get_rect(center=self.rect.center))
        if self.press_t > 0: self.press_t -= 1

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            self.press_t = 8
            return True
        return False

# ─── INPUT BOX ───────────────────────────────────────────
class InputBox:
    def __init__(self, x, y, w, h, font, text="", numeric=False, hint="", label=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = str(text)
        self.numeric = numeric
        self.active = False
        self.font = font
        self.hint = hint
        self.label = label

    def draw(self, surf, font_label=None):
        if self.label and font_label:
            lbl = font_label.render(self.label, True, C_GRAY)
            surf.blit(lbl, (self.rect.x, self.rect.y - 22))
        pygame.draw.rect(surf, (14, 14, 24), self.rect, border_radius=8)
        border_c = C_CYAN if self.active else C_BORDER
        pygame.draw.rect(surf, border_c, self.rect, 2, border_radius=8)
        if self.active:
            draw_rect_alpha(surf, (*C_CYAN, 15), self.rect, radius=8)
        display = self.text if (self.text or self.active) else self.hint
        color = C_WHITE if (self.text or self.active) else C_GRAY
        t_surf = self.font.render(display + ("|" if self.active else ""), True, color)
        surf.blit(t_surf, (self.rect.x + 12, self.rect.y + (self.rect.h - t_surf.get_height()) // 2))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
            elif not self.numeric or event.unicode.isnumeric() or event.unicode in ".-":
                self.text += event.unicode

# ─── HUD BAR ─────────────────────────────────────────────
def draw_hud(surf, font, font_small, t):
    hud_h = 48
    draw_rect_alpha(surf, (0, 0, 0, 190), (0, 0, WIDTH, hud_h))
    # Thin accent line at bottom of HUD
    pygame.draw.line(surf, C_BORDER, (0, hud_h), (WIDTH, hud_h), 1)

    # Status dot
    dot_c = C_GREEN if data_state.is_connected else C_RED
    pulse_r = 6 + int(2 * math.sin(t * 0.1))
    draw_glow_circle(surf, dot_c, (20, hud_h // 2), pulse_r, layers=4)

    # ID / status text
    if data_state.is_connected:
        id_text = font.render(f"LIVE  @{data_state.tiktok_id}", True, C_WHITE)
    else:
        id_text = font.render("WAITING FOR CONNECTION...", True, C_GRAY)
    surf.blit(id_text, (38, hud_h // 2 - id_text.get_height() // 2))

    # Last event (right side)
    ev = data_state.last_event
    if ev:
        ev_surf = font_small.render(ev, True, C_GOLD)
        surf.blit(ev_surf, (WIDTH - ev_surf.get_width() - 14, hud_h // 2 - ev_surf.get_height() // 2))

# ─── DIVIDER ─────────────────────────────────────────────
def draw_divider(surf, sx, shake, font, t):
    x = int(sx + random.uniform(-shake, shake) * 0.5)
    # Glow layers
    for i in range(8, 0, -2):
        a = max(0, 55 - i * 5)
        s = pygame.Surface((i*2+2, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, a), (0, 0, i*2+2, HEIGHT))
        surf.blit(s, (x - i, 0))
    pygame.draw.line(surf, C_WHITE, (x, 0), (x, HEIGHT), 2)
    # Center medallion
    cy = HEIGHT // 2
    draw_glow_circle(surf, C_WHITE, (x, cy), 24, layers=5)
    pygame.draw.circle(surf, C_BG, (x, cy), 20)
    # Animated ring
    ring_r = 17 + int(3 * math.sin(t * 0.08))
    pygame.draw.circle(surf, C_GOLD, (x, cy), ring_r, 2)
    sword = font.render("X", True, C_WHITE)
    surf.blit(sword, sword.get_rect(center=(x, cy)))

# ─── SCORE BAR ───────────────────────────────────────────
def draw_score_bar(surf, font_score, font_label):
    bar_h = 40
    bar_y = HEIGHT - bar_h
    total = max(data_state.score_a + data_state.score_b, 1)
    ratio_a = data_state.score_a / total

    # BG
    pygame.draw.rect(surf, (10, 10, 18), (0, bar_y, WIDTH, bar_h))
    pygame.draw.line(surf, C_BORDER, (0, bar_y), (WIDTH, bar_y), 1)

    split = int(WIDTH * ratio_a)
    if split > 4:
        pygame.draw.rect(surf, C_RED_DIM, (0, bar_y + 1, split, bar_h - 1))
        # Brighter inner strip
        pygame.draw.rect(surf, C_RED, (0, bar_y + 1, split, 4))
    if split < WIDTH - 4:
        pygame.draw.rect(surf, C_BLUE_DIM, (split, bar_y + 1, WIDTH - split, bar_h - 1))
        pygame.draw.rect(surf, C_BLUE, (split, bar_y + 1, WIDTH - split, 4))

    # Divider tick
    pygame.draw.line(surf, C_WHITE, (split, bar_y), (split, HEIGHT), 2)

    # Scores
    sa = font_score.render(str(data_state.score_a), True, C_WHITE)
    sb = font_score.render(str(data_state.score_b), True, C_WHITE)
    surf.blit(sa, (12, bar_y + (bar_h - sa.get_height()) // 2))
    surf.blit(sb, (WIDTH - sb.get_width() - 12, bar_y + (bar_h - sb.get_height()) // 2))

    # Percent
    pct_a = font_label.render(f"{int(ratio_a*100)}%", True, (200,200,200))
    pct_b = font_label.render(f"{int((1-ratio_a)*100)}%", True, (200,200,200))
    surf.blit(pct_a, (split // 2 - pct_a.get_width() // 2, bar_y + (bar_h - pct_a.get_height()) // 2))
    surf.blit(pct_b, (split + (WIDTH-split)//2 - pct_b.get_width()//2, bar_y + (bar_h - pct_b.get_height())//2))

# ─── SETTINGS PAGE ───────────────────────────────────────
def draw_settings_page(surf, boxes, btn_save, btn_back, font_title, font_label, t, scroll_y=0):
    HEADER_H = 70
    FOOTER_H = 70  # quay lại button area

    # ── Scrollable content vẽ lên surface riêng rồi clip ──
    sections = [
        ("LỰC ĐẨY",       [(boxes["p_com"],  "Lực Comment (px/comment)"),
                            (boxes["p_gift"], "Lực Quà (px/gift × số lượng)")]),
        ("COMMENT KÝ TỰ", [(boxes["cmt_a"],  "Ký tự → Đội Đỏ  (VD: 1, A, red...)"),
                            (boxes["cmt_b"],  "Ký tự → Đội Xanh  (VD: 2, B, blue...)")]),
        ("QUÀ TẶNG",      [(boxes["gift_a"], "Tên quà → Đội Đỏ"),
                            (boxes["gift_b"], "Tên quà → Đội Xanh")]),
    ]
    card_x, card_w = 60, WIDTH - 120

    # Tính tổng chiều cao content
    total_h = 16
    for _, items in sections:
        total_h += len(items) * 72 + 44 + 16
    total_h += 60  # nút save

    content_surf = pygame.Surface((WIDTH, max(total_h, HEIGHT)), pygame.SRCALPHA)

    cy = 16
    for sec_title, items in sections:
        card_h = len(items) * 72 + 44
        draw_rect_alpha(content_surf, (20, 20, 34, 200), (card_x, cy, card_w, card_h), radius=14)
        pygame.draw.rect(content_surf, C_BORDER, (card_x, cy, card_w, card_h), 1, border_radius=14)
        sh = font_label.render(sec_title, True, C_CYAN)
        content_surf.blit(sh, (card_x + 18, cy + 12))
        for j, (box, lbl) in enumerate(items):
            by = cy + 44 + j * 72
            box.rect.x = card_x + 18
            box.rect.y = HEADER_H + by - scroll_y  # vị trí thực trên screen để click hoạt động
            box.rect.w = card_w - 36
            lbl_surf = font_label.render(lbl, True, C_GRAY)
            content_surf.blit(lbl_surf, (card_x + 18, by))
            # Vẽ box lên content_surf tại vị trí relative
            box_rel = pygame.Rect(card_x + 18, by + 22, card_w - 36, 40)
            pygame.draw.rect(content_surf, (14, 14, 24), box_rel, border_radius=8)
            border_c = C_CYAN if box.active else C_BORDER
            pygame.draw.rect(content_surf, border_c, box_rel, 2, border_radius=8)
            if box.active:
                draw_rect_alpha(content_surf, (*C_CYAN, 15), box_rel, radius=8)
            display = box.text if box.text else box.hint
            color = C_WHITE if box.text else C_GRAY
            t_surf = box.font.render(display + ("|" if box.active else ""), True, color)
            content_surf.blit(t_surf, (box_rel.x + 12, box_rel.y + (box_rel.h - t_surf.get_height()) // 2))
        cy += card_h + 16

    # Nút save trên content_surf
    save_y_on_content = cy + 8
    save_rect_content = pygame.Rect(card_x, save_y_on_content, card_w, 48)
    btn_save.rect.x = card_x
    btn_save.rect.y = HEADER_H + save_y_on_content - scroll_y
    btn_save.rect.w = card_w
    btn_save.rect.h = 48
    pygame.draw.rect(content_surf, (18, 36, 22), save_rect_content, border_radius=12)
    pygame.draw.rect(content_surf, C_GREEN, save_rect_content, 2, border_radius=12)
    slbl = font_label.render("✔  LƯU CÀI ĐẶT", True, C_WHITE)
    content_surf.blit(slbl, slbl.get_rect(center=save_rect_content.center))

    # Clip và blit vùng scroll (chỉ phần giữa header và footer)
    scroll_area_h = HEIGHT - HEADER_H - FOOTER_H
    surf.blit(content_surf, (0, HEADER_H), (0, scroll_y, WIDTH, scroll_area_h))

    # ── Header cố định (vẽ đè lên) ──
    draw_rect_alpha(surf, (8, 8, 16, 240), (0, 0, WIDTH, HEADER_H))
    pygame.draw.line(surf, C_BORDER, (0, HEADER_H), (WIDTH, HEADER_H), 1)
    title = font_title.render("⚙  CÀI ĐẶT", True, C_WHITE)
    surf.blit(title, (30, 18))

    # ── Footer cố định ──
    draw_rect_alpha(surf, (8, 8, 16, 200), (0, HEIGHT - FOOTER_H, WIDTH, FOOTER_H))
    pygame.draw.line(surf, C_BORDER, (0, HEIGHT - FOOTER_H), (WIDTH, HEIGHT - FOOTER_H), 1)
    btn_back.rect.y = HEIGHT - 52
    btn_back.draw(surf)

    # Scroll indicator
    max_scroll = max(0, total_h - scroll_area_h)
    if max_scroll > 0:
        bar_h = int(scroll_area_h * scroll_area_h / total_h)
        bar_y = HEADER_H + int((scroll_area_h - bar_h) * scroll_y / max_scroll)
        pygame.draw.rect(surf, C_BORDER, (WIDTH - 6, HEADER_H, 4, scroll_area_h), border_radius=2)
        pygame.draw.rect(surf, C_CYAN,   (WIDTH - 6, bar_y,    4, bar_h),          border_radius=2)

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def main():
    font_title  = get_font(46, bold=True)
    font_big    = get_font(54, bold=True)
    font_menu   = get_font(22, bold=True)
    font_text   = get_font(19)
    font_small  = get_font(15)
    font_label  = get_font(14)
    font_score  = get_font(20, bold=True)

    CX = WIDTH // 2
    # ── Menu buttons ──
    btn_start = Button(CX-160, 260, 320, 52, "BẮT ĐẦU LIVE", C_RED,   font_menu, icon=">>")
    btn_test  = Button(CX-160, 326, 320, 52, "CHẾ ĐỘ TEST",  C_GOLD,  font_menu, icon="[T]")
    btn_set   = Button(CX-160, 392, 320, 52, "CÀI ĐẶT",       C_CYAN,  font_menu, icon="[S]")

    btn_save  = Button(60,  0, 840, 48, "LƯU CÀI ĐẶT",    C_GREEN, font_menu, icon="OK")
    btn_back  = Button(20, HEIGHT-56, 160, 40, "← QUAY LẠI", C_GRAY, font_small)
    btn_conn  = Button(CX-160, HEIGHT//2+40, 320, 50, "KẾT NỐI",   C_CYAN,  font_menu, icon=">>")

    id_box = InputBox(CX-200, HEIGHT//2-10, 400, 48, font_text, hint="Nhập ID TikTok của bạn...", label="TikTok ID")

    settings_boxes = {
        "p_com":    InputBox(0, 0, 0, 40, font_text, text="3.0",       numeric=True),
        "p_gift":   InputBox(0, 0, 0, 40, font_text, text="15.0",      numeric=True),
        "cmt_a":    InputBox(0, 0, 0, 40, font_text, text="1"),
        "cmt_b":    InputBox(0, 0, 0, 40, font_text, text="2"),
        "gift_a":   InputBox(0, 0, 0, 40, font_text, text="Rose,TikTok Universe,Lion,Doughnut"),
        "gift_b":   InputBox(0, 0, 0, 40, font_text, text="Ice Cream,Sunglasses,Heart Me,GG"),
    }
    try:
        r_org = pygame.image.load("assets/man.png").convert_alpha()
        b_org = pygame.image.load("assets/woman.png").convert_alpha()
        r_org = pygame.transform.flip(r_org, True, False)
        imgs_ok = True
    except:
        imgs_ok = False

    state = "MENU"
    smooth_split = 480.0
    prev_split = 480.0
    t = 0
    settings_scroll = 0

    while True:
        screen.fill(C_BG)
        dt = clock.tick(60)
        t += 1

        # Lerp smooth divider
        if data_state.shake_intensity > 0:
            data_state.shake_intensity = max(0, data_state.shake_intensity - 0.15)
        smooth_split += (data_state.split_x - smooth_split) * 0.08

        # Particle trigger
        if abs(data_state.split_x - prev_split) > 4:
            color = C_RED if data_state.split_x > prev_split else C_BLUE
            spawn_particles(int(smooth_split), HEIGHT // 2, color, count=14)
        prev_split = data_state.split_x

        # ── Events ──────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if state == "MENU":
                if btn_start.handle(event): state = "CONNECT"
                if btn_test.handle(event):  state = "GAME"
                if btn_set.handle(event):
                    settings_scroll = 0
                    state = "SETTINGS"

            elif state == "CONNECT":
                id_box.handle(event)
                if btn_back.handle(event): state = "MENU"
                if btn_conn.handle(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                    uid = id_box.text.strip()
                    if uid:
                        data_state.tiktok_id = uid
                        threading.Thread(target=start_tiktok_thread, args=(uid,), daemon=True).start()
                        state = "GAME"

            elif state == "SETTINGS":
                for box in settings_boxes.values(): box.handle(event)
                if btn_back.handle(event): state = "MENU"
                if event.type == pygame.MOUSEWHEEL:
                    max_scroll = max(0, (3 * (2*72+44+16) + 16 + 68) - (HEIGHT - 70 - 70))
                    settings_scroll = max(0, min(max_scroll, settings_scroll - event.y * 20))
                if btn_save.handle(event):
                    try: data_state.power_comment = float(settings_boxes["p_com"].text)
                    except: pass
                    try: data_state.power_gift    = float(settings_boxes["p_gift"].text)
                    except: pass
                    if settings_boxes["cmt_a"].text.strip():
                        data_state.team_a_comment = settings_boxes["cmt_a"].text.strip()
                    if settings_boxes["cmt_b"].text.strip():
                        data_state.team_b_comment = settings_boxes["cmt_b"].text.strip()
                    data_state.team_a_gift = settings_boxes["gift_a"].text.strip()
                    data_state.team_b_gift = settings_boxes["gift_b"].text.strip()
                    state = "MENU"

            elif state == "GAME":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: state = "MENU"
                if event.type == pygame.KEYDOWN and event.unicode == data_state.team_a_comment:
                    data_state.split_x = max(50, min(850, data_state.split_x + 25))
                    data_state.score_a += 1; data_state.shake_intensity = 5
                if event.type == pygame.KEYDOWN and event.unicode == data_state.team_b_comment:
                    data_state.split_x = max(50, min(850, data_state.split_x - 25))
                    data_state.score_b += 1; data_state.shake_intensity = 5

        # ── RENDER ──────────────────────────────────────────
        draw_stars(screen, t)

        if state == "MENU":
            # Ambient glow blobs
            for bx, by, bc, br in [(240, 300, C_RED, 200), (720, 300, C_BLUE, 200)]:
                s = pygame.Surface((br*2, br*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*bc, 22), (br, br), br)
                screen.blit(s, (bx - br, by - br))

            draw_animated_title(screen, font_big, font_label, t)

            # Thin horizontal rule
            pygame.draw.line(screen, C_BORDER, (CX-180, 240), (CX+180, 240), 1)

            btn_start.draw(screen, t)
            btn_test.draw(screen, t)
            btn_set.draw(screen, t)

            # Footer hint
            hint = font_label.render("Nhấn ký tự trong game để test thủ công", True, C_GRAY)
            screen.blit(hint, (CX - hint.get_width()//2, HEIGHT - 30))

        elif state == "CONNECT":
            # Ambient glow
            # Ambient glow
            gs = pygame.Surface((480, 480), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*C_CYAN, 14), (240, 240), 240)
            screen.blit(gs, (CX - 240, HEIGHT//2 - 300))

            # ── Title block ──
            title = font_title.render("KẾT NỐI TIKTOK LIVE", True, C_WHITE)
            screen.blit(title, (CX - title.get_width()//2, 80))
            sub = font_small.render("Nhập username, không cần @  -  Ví dụ: yourname", True, C_GRAY)
            screen.blit(sub, (CX - sub.get_width()//2, 134))

            # ── Card ──
            card_x = CX - 260
            card_y = 175
            card_w = 520
            card_h = 260
            draw_rect_alpha(screen, (18, 18, 30, 235), (card_x, card_y, card_w, card_h), radius=16)
            pygame.draw.rect(screen, C_BORDER, (card_x, card_y, card_w, card_h), 1, border_radius=16)
            pygame.draw.rect(screen, C_CYAN, (card_x + 1, card_y + 1, card_w - 2, 3), border_radius=16)

            # Label
            lbl = font_label.render("TIKTOK USERNAME", True, C_CYAN)
            screen.blit(lbl, (card_x + 24, card_y + 22))

            # Input box
            id_box.rect = pygame.Rect(card_x + 20, card_y + 50, card_w - 40, 54)
            id_box.draw(screen)

            # Divider
            pygame.draw.line(screen, C_BORDER,
                             (card_x + 20, card_y + 122), (card_x + card_w - 20, card_y + 122), 1)

            # Connect button — clear space below divider
            btn_conn.rect = pygame.Rect(card_x + 20, card_y + 140, card_w - 40, 52)
            btn_conn.draw(screen, t)

            # Hint below card
            hint = font_label.render("Hoặc nhấn  ENTER  để kết nối", True, C_GRAY)
            screen.blit(hint, (CX - hint.get_width()//2, card_y + card_h + 14))

            btn_back.rect.y = HEIGHT - 52
            btn_back.draw(screen, t)

        elif state == "SETTINGS":
            draw_settings_page(screen, settings_boxes, btn_save, btn_back,
                               font_title, font_label, t, scroll_y=settings_scroll)

        elif state == "GAME":
            sx = int(smooth_split)
            # Backgrounds
            pygame.draw.rect(screen, (35, 8, 12), (0, 0, sx, HEIGHT))
            pygame.draw.rect(screen, (8, 12, 40), (sx, 0, WIDTH, HEIGHT))
            # Subtle gradient vignette
            for side, col, rx in [("L", C_RED, 0), ("R", C_BLUE, sx)]:
                gs = pygame.Surface((min(sx, WIDTH-sx), HEIGHT), pygame.SRCALPHA)
                for xi in range(0, min(sx, WIDTH-sx), 4):
                    a = int(30 * (1 - xi / max(min(sx, WIDTH-sx), 1)))
                    pygame.draw.line(gs, (*col, a), (xi if side=="L" else min(sx,WIDTH-sx)-xi, 0),
                                     (xi if side=="L" else min(sx,WIDTH-sx)-xi, HEIGHT))
                screen.blit(gs, (sx - min(sx,WIDTH-sx) if side=="L" else sx, 0))

            # Character images
            if imgs_ok:
                rf = max(1.0, 1.0 + (smooth_split - 480)/480 * 0.6)
                bf = max(1.0, 1.0 + (480 - smooth_split)/480 * 0.6)
                ri = pygame.transform.smoothscale(r_org, (int(260*rf), int(260*rf)))
                bi = pygame.transform.smoothscale(b_org, (int(260*bf), int(260*bf)))
                screen.blit(ri, (sx//2 - ri.get_width()//2, HEIGHT//2 - ri.get_height()//2 - 20))
                screen.blit(bi, (sx + (WIDTH-sx)//2 - bi.get_width()//2, HEIGHT//2 - bi.get_height()//2 - 20))

            update_draw_particles(screen)
            draw_divider(screen, smooth_split, data_state.shake_intensity, font_menu, t)
            draw_score_bar(screen, font_score, font_label)
            draw_hud(screen, font_menu, font_small, t)

            # Team labels
            rl = font_menu.render("RED TEAM", True, C_RED)
            bl = font_menu.render("BLUE TEAM", True, C_BLUE)
            screen.blit(rl, (sx//2 - rl.get_width()//2, HEIGHT - 75))
            screen.blit(bl, (sx + (WIDTH-sx)//2 - bl.get_width()//2, HEIGHT - 75))

            # ESC hint — hiển thị ký tự hiện tại từ settings
            hint_txt = f"ESC = Menu  |  '{data_state.team_a_comment}' = Red Team  |  '{data_state.team_b_comment}' = Blue Team"
            esc = font_label.render(hint_txt, True, C_GRAY)
            screen.blit(esc, (WIDTH//2 - esc.get_width()//2, HEIGHT - 56))

        pygame.display.flip()

if __name__ == "__main__":
    main()