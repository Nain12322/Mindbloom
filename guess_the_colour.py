"""
=============================================================================
MINDBLOOM: GUESS THE COLOUR
A Dementia-Friendly Object & Colour Recognition Game for Memory Garden
Inspired by the MindBloom UI and enriched with procedural Quiet FX audio cues.

Features:
- Starts with Black & White (Grayscale) photos for cognitive memory stimulation
- Interactive Color Reveal: blooming smoothly into vibrant full color upon choice
- Mystery clues that never spoil the answer before guessing
- Dementia-friendly non-punitive gentle guidance and Quiet FX sound cues

Run standalone:
    python guess_the_colour.py

Import into MindBloom GUI:
    from guess_the_colour import GuessTheColourGame
    game = GuessTheColourGame(screen)
    game.run()
=============================================================================
"""

import math
import random
import sys
import pygame

# Import embedded assets (photos and quiet-fx sound effects)
try:
    import color_assets
except ImportError:
    color_assets = None

# ---------------------------------------------------------------------------
# DEFAULT CONFIGURATION & PALETTE
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1280, 720
FPS = 60

COLOR_BG = (8, 27, 70)           # Deep calm navy
COLOR_GRID = (18, 43, 91)        # Soothing background grid lines
COLOR_WHITE = (250, 252, 255)    # Clean off-white
COLOR_SHADOW = (3, 12, 35)       # Soft drop shadow

COLOR_PURPLE = (116, 70, 224)
COLOR_PURPLE_DARK = (81, 46, 164)
COLOR_CARD_BLUE = (55, 145, 239)
COLOR_CARD_BLUE_DARK = (30, 95, 175)
COLOR_GREEN = (47, 190, 112)
COLOR_YELLOW = (255, 207, 66)
COLOR_CORAL = (235, 75, 75)

COLOR_MAP = {
    "Red": {
        "swatch": (225, 45, 45),
        "dark": (160, 25, 25),
        "text_color": COLOR_WHITE,
    },
    "Yellow": {
        "swatch": (250, 205, 40),
        "dark": (180, 145, 20),
        "text_color": (30, 30, 30),
    },
    "Orange": {
        "swatch": (245, 125, 30),
        "dark": (175, 80, 15),
        "text_color": COLOR_WHITE,
    },
    "Green": {
        "swatch": (45, 185, 80),
        "dark": (25, 130, 50),
        "text_color": COLOR_WHITE,
    },
    "Purple": {
        "swatch": (145, 75, 215),
        "dark": (95, 40, 155),
        "text_color": COLOR_WHITE,
    },
    "Blue": {
        "swatch": (45, 125, 240),
        "dark": (25, 80, 170),
        "text_color": COLOR_WHITE,
    },
    "Pink": {
        "swatch": (245, 115, 175),
        "dark": (180, 60, 120),
        "text_color": COLOR_WHITE,
    },
    "White": {
        "swatch": (245, 248, 255),
        "dark": (195, 205, 220),
        "text_color": (25, 35, 60),
    },
}

ITEMS_CATALOG = [
    {
        "id": "strawberry",
        "mystery_name": "Summer Berry",
        "revealed_name": "Red Strawberry",
        "category": "Fruit",
        "color": "Red",
    },
    {
        "id": "sunflower",
        "mystery_name": "Sun-Facing Flower",
        "revealed_name": "Yellow Sunflower",
        "category": "Flower",
        "color": "Yellow",
    },
    {
        "id": "orange_fruit",
        "mystery_name": "Citrus Fruit",
        "revealed_name": "Juicy Orange",
        "category": "Fruit",
        "color": "Orange",
    },
    {
        "id": "purple_lavender",
        "mystery_name": "Fragrant Blossom",
        "revealed_name": "Purple Lavender",
        "category": "Flower",
        "color": "Purple",
    },
    {
        "id": "green_apple",
        "mystery_name": "Orchard Apple",
        "revealed_name": "Green Apple",
        "category": "Fruit",
        "color": "Green",
    },
    {
        "id": "blue_blueberries",
        "mystery_name": "Sweet Berries",
        "revealed_name": "Blue Blueberries",
        "category": "Fruit",
        "color": "Blue",
    },
    {
        "id": "pink_cherry_blossom",
        "mystery_name": "Spring Sakura Branch",
        "revealed_name": "Pink Cherry Blossom",
        "category": "Flower",
        "color": "Pink",
    },
    {
        "id": "white_daisy",
        "mystery_name": "Meadow Flower",
        "revealed_name": "White Daisy",
        "category": "Flower",
        "color": "White",
    },
]

# ---------------------------------------------------------------------------
# FONT HELPER
# ---------------------------------------------------------------------------
FONT_CACHE = {}

def get_font(size, bold=False):
    key = (size, bold)
    if key in FONT_CACHE:
        return FONT_CACHE[key]
    font_obj = None
    for candidate in ["segoeui", "arial", "dejavusans", "liberationsans"]:
        path = pygame.font.match_font(candidate, bold=bold)
        if path:
            try:
                font_obj = pygame.font.Font(path, size)
                break
            except Exception:
                pass
    if font_obj is None:
        font_obj = pygame.font.Font(None, size)
    FONT_CACHE[key] = font_obj
    return font_obj

# ---------------------------------------------------------------------------
# PARTICLES & CELEBRATION STARS
# ---------------------------------------------------------------------------
class StarParticle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2.5, 7.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 2.5
        self.radius = random.uniform(6, 12)
        self.alpha = 255
        self.decay = random.uniform(2.0, 4.0)
        self.is_star = random.choice([True, False])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.alpha = max(0, self.alpha - self.decay)
        self.radius = max(1.0, self.radius - 0.05)
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha <= 0:
            return
        draw_col = tuple(min(255, c) for c in self.color)
        pos = (int(self.x), int(self.y))
        if self.is_star:
            draw_star(surface, pos, int(self.radius), draw_col)
        else:
            pygame.draw.circle(surface, draw_col, pos, int(self.radius))

def draw_star(surface, center, radius, color):
    points = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = radius if i % 2 == 0 else radius * 0.45
        points.append((center[0] + math.cos(angle) * r, center[1] + math.sin(angle) * r))
    if len(points) >= 3:
        pygame.draw.polygon(surface, color, points)

# ---------------------------------------------------------------------------
# UI DRAWING ROUTINES
# ---------------------------------------------------------------------------
def draw_mindbloom_background(surface):
    w, h = surface.get_size()
    surface.fill(COLOR_BG)
    spacing = max(24, int(min(w, h) * 0.035))
    for x in range(0, w, spacing):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, h), 1)
    for y in range(0, h, spacing):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (w, y), 1)

def draw_tactile_button(surface, rect, base_color, border_color=COLOR_WHITE, radius=18, hover=False, clicked=False):
    shadow_offset = 3 if clicked else (6 if hover else 4)
    shadow_rect = pygame.Rect(rect.x, rect.y + shadow_offset, rect.width, rect.height)
    pygame.draw.rect(surface, COLOR_SHADOW, shadow_rect, border_radius=radius)

    body_color = base_color
    if hover and not clicked:
        body_color = tuple(min(255, c + 18) for c in base_color)
    elif clicked:
        body_color = tuple(max(0, c - 15) for c in base_color)

    draw_rect = rect.copy()
    if clicked:
        draw_rect.y += 2

    pygame.draw.rect(surface, body_color, draw_rect, border_radius=radius)
    pygame.draw.rect(surface, border_color, draw_rect, width=3, border_radius=radius)
    return draw_rect

def draw_header_banner(surface, rect, title="MindBloom - Guess the Colour"):
    shadow_rect = rect.copy()
    shadow_rect.y += 5
    pygame.draw.rect(surface, COLOR_PURPLE_DARK, shadow_rect, border_radius=rect.height // 2)

    pygame.draw.rect(surface, COLOR_PURPLE, rect, border_radius=rect.height // 2)
    pygame.draw.rect(surface, (170, 135, 255), rect, width=3, border_radius=rect.height // 2)

    icon_size = int(rect.height * 0.65)
    icon_rect = pygame.Rect(rect.x + 18, rect.centery - icon_size // 2, icon_size, icon_size)
    pygame.draw.rect(surface, COLOR_WHITE, icon_rect, border_radius=8)

    inner = icon_rect.inflate(-8, -8)
    pygame.draw.rect(surface, COLOR_CARD_BLUE, inner, border_radius=6)
    pygame.draw.circle(surface, COLOR_YELLOW, inner.center, max(4, inner.width // 4))

    fnt = get_font(max(18, int(rect.height * 0.44)), bold=True)
    text_surf = fnt.render(title, True, COLOR_WHITE)
    surface.blit(text_surf, text_surf.get_rect(center=(rect.centerx + 12, rect.centery)))

def draw_home_button(surface, rect, hover=False):
    shadow = rect.copy()
    shadow.y += 4 if not hover else 6
    pygame.draw.ellipse(surface, COLOR_SHADOW, shadow)

    col = COLOR_CARD_BLUE if not hover else tuple(min(255, c + 20) for c in COLOR_CARD_BLUE)
    pygame.draw.ellipse(surface, col, rect)
    pygame.draw.ellipse(surface, (130, 205, 255), rect, width=3)

    cx, cy = rect.center
    sz = rect.width * 0.35
    roof = [
        (cx, cy - sz * 0.55),
        (cx - sz * 0.72, cy),
        (cx - sz * 0.48, cy),
        (cx - sz * 0.48, cy + sz * 0.58),
        (cx + sz * 0.48, cy + sz * 0.58),
        (cx + sz * 0.48, cy),
        (cx + sz * 0.72, cy),
    ]
    pygame.draw.polygon(surface, COLOR_WHITE, roof)
    door = pygame.Rect(cx - sz * 0.16, cy + sz * 0.1, sz * 0.32, sz * 0.48)
    pygame.draw.rect(surface, (50, 110, 190), door)

def draw_sound_toggle(surface, rect, is_on, hover=False):
    shadow = rect.copy()
    shadow.y += 4
    pygame.draw.ellipse(surface, COLOR_SHADOW, shadow)

    col = (50, 120, 210) if is_on else (120, 130, 150)
    if hover:
        col = tuple(min(255, c + 20) for c in col)
    pygame.draw.ellipse(surface, col, rect)
    pygame.draw.ellipse(surface, COLOR_WHITE, rect, width=2)

    cx, cy = rect.center
    sz = int(rect.width * 0.28)
    cone = [
        (cx - sz, cy - sz // 2),
        (cx - sz // 3, cy - sz // 2),
        (cx + sz // 3, cy - sz),
        (cx + sz // 3, cy + sz),
        (cx - sz // 3, cy + sz // 2),
        (cx - sz, cy + sz // 2),
    ]
    pygame.draw.polygon(surface, COLOR_WHITE, cone)

    if is_on:
        pygame.draw.arc(surface, COLOR_YELLOW, (cx - sz // 2, cy - sz, sz * 2, sz * 2), -math.pi / 3, math.pi / 3, 3)
    else:
        pygame.draw.line(surface, COLOR_CORAL, (cx - sz, cy - sz), (cx + sz, cy + sz), 3)

def draw_score_pill(surface, rect, score):
    shadow = rect.copy()
    shadow.y += 4
    pygame.draw.rect(surface, (10, 35, 75), shadow, border_radius=rect.height // 2)
    pygame.draw.rect(surface, (20, 60, 125), rect, border_radius=rect.height // 2)
    pygame.draw.rect(surface, (80, 165, 255), rect, width=3, border_radius=rect.height // 2)

    star_radius = int(rect.height * 0.26)
    star_center = (rect.x + star_radius * 2, rect.centery)
    draw_star(surface, star_center, star_radius, COLOR_YELLOW)

    fnt = get_font(max(16, int(rect.height * 0.40)), bold=True)
    txt = f"Score: {score}"
    text_surf = fnt.render(txt, True, COLOR_WHITE)
    surface.blit(text_surf, (rect.x + star_radius * 3.6, rect.centery - text_surf.get_height() // 2))

# ---------------------------------------------------------------------------
# MAIN GAME CLASS
# ---------------------------------------------------------------------------
class GuessTheColourGame:
    def __init__(self, surface=None):
        if surface is None:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            self.owns_display = True
        else:
            self.screen = surface
            self.owns_display = False

        self.clock = pygame.time.Clock()
        self.sound_enabled = True
        self.sounds = {}
        self.init_audio()

        self.score = 0
        self.streak = 0
        self.high_score = 0

        self.particles = []
        self.items = ITEMS_CATALOG
        self.images_color = {}
        self.images_bw = {}
        self.load_images()

        self.current_item_index = 0
        self.mcq_options = []
        self.selected_option = None
        self.feedback_message = ""
        self.feedback_color = COLOR_WHITE
        self.is_answered = False
        self.answer_is_correct = False
        self.is_revealed = False
        self.reveal_progress = 0.0
        self.advance_timer = 0
        self.last_hovered_id = None

    def init_audio(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            if color_assets:
                for snd_name in ["correct", "bloom", "celebrate", "gentle_hint", "hover", "click", "tap"]:
                    s = color_assets.load_sound(snd_name)
                    if s:
                        s.set_volume(0.45)
                        self.sounds[snd_name] = s
        except Exception as e:
            print(f"Audio init notice: {e}")
            self.sound_enabled = False

    def play_sound(self, name):
        if not self.sound_enabled:
            return
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def load_images(self):
        for item in self.items:
            item_id = item["id"]
            surf_color = None
            if color_assets:
                surf_color = color_assets.load_image(item_id)

            if surf_color is None:
                # Procedural fallback
                surf_color = pygame.Surface((400, 400), pygame.SRCALPHA)
                col = COLOR_MAP.get(item["color"], {}).get("swatch", (200, 200, 200))
                pygame.draw.circle(surf_color, col, (200, 200), 140)
                pygame.draw.circle(surf_color, (255, 255, 255), (200, 200), 140, 8)
                fnt = get_font(30, bold=True)
                txt = fnt.render(item["mystery_name"], True, (255, 255, 255))
                surf_color.blit(txt, txt.get_rect(center=(200, 200)))

            try:
                surf_bw = pygame.transform.grayscale(surf_color)
            except Exception:
                surf_bw = surf_color.copy()

            self.images_color[item_id] = surf_color
            self.images_bw[item_id] = surf_bw

    def setup_round(self):
        self.current_item = self.items[self.current_item_index]
        correct_color = self.current_item["color"]

        all_colors = list(COLOR_MAP.keys())
        wrong_colors = [c for c in all_colors if c != correct_color]
        chosen_wrongs = random.sample(wrong_colors, 3)

        self.mcq_options = [correct_color] + chosen_wrongs
        random.shuffle(self.mcq_options)

        self.selected_option = None
        self.is_answered = False
        self.answer_is_correct = False
        self.is_revealed = False
        self.reveal_progress = 0.0

        cat = self.current_item["category"].lower()
        self.feedback_message = f"Can you guess the natural colour of this {cat}?"
        self.feedback_color = COLOR_WHITE
        self.advance_timer = 0

    def trigger_celebration(self, center_pos):
        colors = [COLOR_YELLOW, COLOR_GREEN, COLOR_CARD_BLUE, COLOR_WHITE, COLOR_PURPLE]
        for _ in range(45):
            c = random.choice(colors)
            self.particles.append(StarParticle(center_pos[0], center_pos[1], c))

    def handle_choice(self, chosen_color, rect_center):
        if self.is_answered and self.answer_is_correct:
            return

        self.selected_option = chosen_color
        correct_color = self.current_item["color"]

        if chosen_color == correct_color:
            self.play_sound("correct")
            self.play_sound("bloom")
            self.is_answered = True
            self.answer_is_correct = True
            self.is_revealed = True
            self.score += 10
            self.streak += 1
            if self.score > self.high_score:
                self.high_score = self.score

            encouragements = [
                f"✨ Wonderful! You revealed the vibrant {correct_color}! ✨",
                f"🌸 Splendid! Look at the {self.current_item['revealed_name']} bloom! 🌸",
                f"🎉 Spot on! It blooms in gorgeous {correct_color}! 🎉",
                f"✨ Beautiful memory! That's a lovely {correct_color}! ✨",
            ]
            self.feedback_message = random.choice(encouragements)
            self.feedback_color = COLOR_YELLOW
            self.trigger_celebration(rect_center)
            self.advance_timer = pygame.time.get_ticks() + 3200
        else:
            self.play_sound("gentle_hint")
            gentle_prompts = [
                f"Good thought! Look closely at the shape — is it {correct_color} or {chosen_color}?",
                f"Almost! It blooms in bright {correct_color}. Try once more to reveal its colours!",
                f"That's a pretty colour! Let's find the matching colour together.",
            ]
            self.feedback_message = random.choice(gentle_prompts)
            self.feedback_color = (255, 230, 130)

    def reveal_manually(self):
        if not self.is_revealed:
            self.play_sound("bloom")
            self.is_revealed = True
            self.is_answered = True
            self.feedback_message = f"🌸 Revealed! This is the {self.current_item['revealed_name']}! 🌸"
            self.feedback_color = COLOR_YELLOW
            w, h = self.screen.get_size()
            self.trigger_celebration((w // 2, h // 2))
            self.advance_timer = pygame.time.get_ticks() + 3200

    def advance_to_next(self):
        self.current_item_index = (self.current_item_index + 1) % len(self.items)
        self.setup_round()

    def run(self):
        running = True
        self.setup_round()

        while running:
            dt_ms = self.clock.tick(FPS)
            dt_sec = dt_ms / 1000.0
            mouse_pos = pygame.mouse.get_pos()
            current_time = pygame.time.get_ticks()
            width, height = self.screen.get_size()

            if self.is_revealed and self.reveal_progress < 1.0:
                self.reveal_progress = min(1.0, self.reveal_progress + dt_sec * 1.6)
                if random.random() < 0.25:
                    card_size = min(max(230, int(height * 0.38)), 320)
                    cx = width // 2 + random.randint(-card_size // 2, card_size // 2)
                    cy = int(height * 0.18) + random.randint(0, card_size)
                    self.particles.append(StarParticle(cx, cy, COLOR_YELLOW))

            if self.is_answered and self.advance_timer > 0 and current_time >= self.advance_timer:
                self.advance_to_next()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_m:
                        self.sound_enabled = not self.sound_enabled
                    elif event.key == pygame.K_r:
                        self.reveal_manually()
                    elif event.key == pygame.K_SPACE:
                        self.advance_to_next()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    bar_h = max(55, int(height * 0.08))
                    home_rect = pygame.Rect(26, 16, bar_h - 4, bar_h - 4)
                    sound_rect = pygame.Rect(width - 26 - (bar_h - 4), 16, bar_h - 4, bar_h - 4)

                    if home_rect.collidepoint(mouse_pos):
                        self.play_sound("click")
                        self.advance_to_next()
                        continue

                    if sound_rect.collidepoint(mouse_pos):
                        self.sound_enabled = not self.sound_enabled
                        continue

                    for b_rect, color_name in getattr(self, "current_mcq_rects", []):
                        if b_rect.collidepoint(mouse_pos):
                            self.handle_choice(color_name, b_rect.center)
                            break

                    reveal_rect = getattr(self, "current_reveal_rect", None)
                    if reveal_rect and reveal_rect.collidepoint(mouse_pos):
                        self.reveal_manually()

                    next_rect = getattr(self, "current_next_rect", None)
                    if next_rect and next_rect.collidepoint(mouse_pos):
                        self.play_sound("tap")
                        self.advance_to_next()

            # Rendering
            draw_mindbloom_background(self.screen)

            # Top bar
            bar_h = max(55, int(height * 0.08))
            home_rect = pygame.Rect(26, 16, bar_h - 4, bar_h - 4)
            draw_home_button(self.screen, home_rect, hover=home_rect.collidepoint(mouse_pos))

            title_w = min(max(320, int(width * 0.38)), 520)
            title_rect = pygame.Rect((width - title_w) // 2, 16, title_w, bar_h - 4)
            draw_header_banner(self.screen, title_rect, "MindBloom - Guess the Colour")

            sound_rect = pygame.Rect(width - 26 - (bar_h - 4), 16, bar_h - 4, bar_h - 4)
            draw_sound_toggle(self.screen, sound_rect, self.sound_enabled, hover=sound_rect.collidepoint(mouse_pos))

            score_w = max(150, int(width * 0.15))
            score_rect = pygame.Rect(sound_rect.left - score_w - 14, 16, score_w, bar_h - 4)
            draw_score_pill(self.screen, score_rect, self.score)

            # Question Text
            q_y = int(height * 0.12)
            fnt_q = get_font(max(24, int(height * 0.038)), bold=True)
            q_surf = fnt_q.render(self.feedback_message, True, self.feedback_color)
            self.screen.blit(q_surf, q_surf.get_rect(center=(width // 2, q_y)))

            # Image Card
            item = self.current_item
            card_size = min(max(230, int(height * 0.38)), 320)
            card_rect = pygame.Rect((width - card_size) // 2, int(height * 0.18), card_size, card_size)

            shadow = card_rect.copy()
            shadow.y += 8
            pygame.draw.rect(self.screen, COLOR_SHADOW, shadow, border_radius=22)
            pygame.draw.rect(self.screen, (22, 38, 80), card_rect, border_radius=22)

            raw_bw = self.images_bw.get(item["id"])
            raw_col = self.images_color.get(item["id"])
            inner_padding = 16
            inner_rect = card_rect.inflate(-inner_padding * 2, -inner_padding * 2)

            if raw_bw:
                scaled_bw = pygame.transform.smoothscale(raw_bw, (inner_rect.width, inner_rect.height))
                self.screen.blit(scaled_bw, inner_rect)

            if self.reveal_progress > 0.0 and raw_col:
                scaled_col = pygame.transform.smoothscale(raw_col, (inner_rect.width, inner_rect.height)).convert_alpha()
                alpha_val = int(min(255, max(0, self.reveal_progress * 255)))
                scaled_col.set_alpha(alpha_val)
                self.screen.blit(scaled_col, inner_rect)

            pygame.draw.rect(self.screen, COLOR_WHITE, card_rect, width=4, border_radius=22)

            if self.reveal_progress > 0.1:
                col_info = COLOR_MAP.get(item["color"], {})
                glow_col = col_info.get("swatch", COLOR_YELLOW)
                glow_rect = card_rect.inflate(6, 6)
                pygame.draw.rect(self.screen, glow_col, glow_rect, width=3, border_radius=24)

            # Name Badge
            badge_w = min(max(280, int(card_size * 1.05)), 350)
            name_badge_rect = pygame.Rect(card_rect.centerx - badge_w // 2, card_rect.bottom - 22, badge_w, 44)

            if not self.is_revealed or self.reveal_progress < 0.2:
                draw_tactile_button(self.screen, name_badge_rect, (24, 45, 95), border_color=COLOR_WHITE, radius=22)
                fnt_name = get_font(18, bold=True)
                name_surf = fnt_name.render(f"🔍 {item['mystery_name']}", True, (225, 235, 255))
                self.screen.blit(name_surf, name_surf.get_rect(center=name_badge_rect.center))
            else:
                col_info = COLOR_MAP.get(item["color"], {})
                badge_bg = col_info.get("dark", COLOR_CARD_BLUE)
                border_col = col_info.get("swatch", COLOR_YELLOW)
                draw_tactile_button(self.screen, name_badge_rect, badge_bg, border_color=border_col, radius=22)
                fnt_name = get_font(18, bold=True)
                name_surf = fnt_name.render(f"✨ {item['revealed_name']}! ✨", True, COLOR_WHITE)
                self.screen.blit(name_surf, name_surf.get_rect(center=name_badge_rect.center))

            # MCQ Buttons
            btn_start_y = int(height * 0.68)
            content_w = min(int(width * 0.86), 960)
            btn_w = (content_w - 60) // 4
            btn_h = min(max(75, int(height * 0.12)), 95)
            start_x = (width - content_w) // 2

            self.current_mcq_rects = []
            for i, color_name in enumerate(self.mcq_options):
                bx = start_x + i * (btn_w + 20)
                b_rect = pygame.Rect(bx, btn_start_y, btn_w, btn_h)
                hover = b_rect.collidepoint(mouse_pos)

                if hover and self.last_hovered_id != f"mcq_{i}":
                    self.play_sound("hover")
                    self.last_hovered_id = f"mcq_{i}"

                color_info = COLOR_MAP.get(color_name, {})
                swatch_col = color_info.get("swatch", (200, 200, 200))
                is_chosen = (self.selected_option == color_name)

                btn_base = (30, 48, 98)
                border_col = COLOR_WHITE
                if is_chosen:
                    if self.answer_is_correct:
                        btn_base = COLOR_GREEN
                        border_col = COLOR_YELLOW
                    else:
                        btn_base = (180, 80, 40)
                        border_col = (255, 180, 80)
                elif self.is_revealed and color_name == item["color"]:
                    btn_base = (40, 110, 65)
                    border_col = COLOR_GREEN

                draw_tactile_button(self.screen, b_rect, btn_base, border_color=border_col, radius=18, hover=hover, clicked=is_chosen)

                swatch_size = int(btn_h * 0.44)
                swatch_center = (b_rect.x + swatch_size + 14, b_rect.centery)
                pygame.draw.circle(self.screen, swatch_col, swatch_center, swatch_size // 2)
                pygame.draw.circle(self.screen, COLOR_WHITE, swatch_center, swatch_size // 2, 2)

                fnt_opt = get_font(max(18, int(btn_h * 0.28)), bold=True)
                opt_surf = fnt_opt.render(color_name.upper(), True, COLOR_WHITE)
                self.screen.blit(opt_surf, (swatch_center[0] + swatch_size // 2 + 12, b_rect.centery - opt_surf.get_height() // 2))

                self.current_mcq_rects.append((b_rect, color_name))

            # Action Buttons
            btn_action_w = 170
            btn_action_h = 44
            action_y = height - 65

            self.current_reveal_rect = None
            if not self.is_revealed:
                self.current_reveal_rect = pygame.Rect(width // 2 - btn_action_w - 12, action_y, btn_action_w, btn_action_h)
                rev_hover = self.current_reveal_rect.collidepoint(mouse_pos)
                draw_tactile_button(self.screen, self.current_reveal_rect, (120, 75, 175), border_color=COLOR_WHITE, radius=22, hover=rev_hover)
                fnt_rev = get_font(15, bold=True)
                rev_surf = fnt_rev.render("REVEAL COLOUR 🌸", True, COLOR_WHITE)
                self.screen.blit(rev_surf, rev_surf.get_rect(center=self.current_reveal_rect.center))

                self.current_next_rect = pygame.Rect(width // 2 + 12, action_y, btn_action_w, btn_action_h)
                next_txt = "SKIP ❯"
            else:
                self.current_next_rect = pygame.Rect(width // 2 - btn_action_w // 2, action_y, btn_action_w, btn_action_h)
                next_txt = "NEXT ▶"

            next_hover = self.current_next_rect.collidepoint(mouse_pos)
            next_base = COLOR_GREEN if self.is_revealed else (70, 100, 170)
            draw_tactile_button(self.screen, self.current_next_rect, next_base, border_color=COLOR_WHITE, radius=22, hover=next_hover)
            fnt_next = get_font(16, bold=True)
            next_surf = fnt_next.render(next_txt, True, COLOR_WHITE)
            self.screen.blit(next_surf, next_surf.get_rect(center=self.current_next_rect.center))

            # Particles
            self.particles = [p for p in self.particles if p.update()]
            for p in self.particles:
                p.draw(self.screen)

            pygame.display.flip()

        if self.owns_display:
            pygame.quit()
            sys.exit()
        return "menu"

if __name__ == "__main__":
    pygame.init()
    game = GuessTheColourGame()
    game.run()
