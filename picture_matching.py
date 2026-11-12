import os
import sys
import random
import math
import pygame

pygame.init()
pygame.display.set_caption("MindBloom - Picture Matching")

screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
clock = pygame.time.Clock()
FPS = 60

# ------------------------- COLORS --------------------------
BG = (8, 27, 70)
GRID = (18, 43, 91)
WHITE = (250, 252, 255)
PURPLE = (116, 70, 224)
PURPLE_DARK = (81, 46, 164)
CARD_BLUE = (55, 145, 239)
GREEN = (47, 190, 112)
YELLOW = (255, 207, 66)
SHADOW = (3, 12, 35)

# ------------------------- SETTINGS ------------------------
PHOTO_FOLDER = "pictures"
MAX_PAIRS = 8
TOTAL_CARDS = 16
CARD_FLIP_TIME = 0.18
WRONG_SHOW_TIME = 0.65
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".jfif", ".webp", ".bmp", ".gif")

# ------------------------- FONTS ----------------------------
font_cache = {}


def font(size, bold=False):
    key = (size, bold)
    if key in font_cache:
        return font_cache[key]

    f = None
    for name in ["arial", "segoeui", "dejavusans", "liberationsans"]:
        path = pygame.font.match_font(name, bold=bold)
        if path:
            f = pygame.font.Font(path, size)
            break
    if f is None:
        f = pygame.font.Font(None, size)

    font_cache[key] = f
    return f


# ------------------------- HELPERS --------------------------
def resource_path(relative):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)


def rounded_rect(surface, color, rect, radius=18):
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_text_center(surface, text, fnt, color, center):
    image = fnt.render(text, True, color)
    surface.blit(image, image.get_rect(center=center))


def draw_grid_background(surface):
    surface.fill(BG)
    w, h = surface.get_size()
    spacing = max(24, int(min(w, h) * 0.032))
    for x in range(0, w, spacing):
        pygame.draw.line(surface, GRID, (x, 0), (x, h), 1)
    for y in range(0, h, spacing):
        pygame.draw.line(surface, GRID, (0, y), (w, y), 1)


def draw_star(surface, center, radius, color):
    points = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = radius if i % 2 == 0 else radius * 0.42
        points.append((center[0] + math.cos(angle) * r,
                       center[1] + math.sin(angle) * r))
    pygame.draw.polygon(surface, color, points)


def draw_home_button(surface, rect):
    shadow = rect.copy()
    shadow.y += 5
    pygame.draw.ellipse(surface, SHADOW, shadow)
    pygame.draw.ellipse(surface, (43, 139, 242), rect)
    pygame.draw.ellipse(surface, (113, 193, 255), rect, width=3)

    cx, cy = rect.center
    size = rect.width * 0.34
    roof = [
        (cx, cy - size * 0.55),
        (cx - size * 0.72, cy),
        (cx - size * 0.48, cy),
        (cx - size * 0.48, cy + size * 0.58),
        (cx + size * 0.48, cy + size * 0.58),
        (cx + size * 0.48, cy),
        (cx + size * 0.72, cy),
    ]
    pygame.draw.polygon(surface, WHITE, roof)
    door = pygame.Rect(cx - size * 0.14, cy + size * 0.08,
                       size * 0.28, size * 0.50)
    pygame.draw.rect(surface, (68, 139, 215), door)


def draw_score(surface, rect, score):
    rounded_rect(surface, (12, 47, 99), rect, rect.height // 2)
    pygame.draw.rect(surface, (68, 160, 250), rect, width=3,
                     border_radius=rect.height // 2)

    star_radius = int(rect.height * 0.25)
    draw_star(surface, (rect.x + star_radius * 1.7, rect.centery),
              star_radius, YELLOW)

    fnt = font(max(20, int(rect.height * 0.35)), True)
    draw_text_center(surface, f"Score: {score}", fnt, WHITE,
                     (rect.x + rect.width * 0.66, rect.centery))


def draw_title(surface, rect):
    shadow = rect.copy()
    shadow.y += 7
    rounded_rect(surface, PURPLE_DARK, shadow, 35)
    rounded_rect(surface, PURPLE, rect, 35)
    pygame.draw.rect(surface, (174, 133, 255), rect, width=3,
                     border_radius=35)

    icon_size = int(rect.height * 0.68)
    icon = pygame.Rect(rect.x + 34, rect.centery - icon_size // 2,
                       icon_size, icon_size)
    rounded_rect(surface, WHITE, icon, 10)

    inner = icon.inflate(-12, -12)
    rounded_rect(surface, (71, 159, 238), inner, 7)

    pygame.draw.polygon(surface, (52, 177, 104), [
        (inner.left + 5, inner.bottom - 7),
        (inner.centerx - 3, inner.centery - 1),
        (inner.centerx + 6, inner.centery + 6),
        (inner.right - 5, inner.top + 9),
        (inner.right - 5, inner.bottom - 7),
    ])
    pygame.draw.circle(surface, YELLOW,
                       (inner.right - 13, inner.top + 13), 6)

    title_font = font(max(30, min(62, int(rect.height * 0.48))), True)
    draw_text_center(surface, "Picture Matching", title_font, WHITE,
                     (rect.centerx + 35, rect.centery))


# --------------------- IMAGE FUNCTIONS ----------------------
def find_images():
    folder = resource_path(PHOTO_FOLDER)

    if not os.path.exists(folder):
        os.makedirs(folder)

    files = []
    for root, dirs, names in os.walk(folder):
        for name in names:
            if name.lower().endswith(IMAGE_EXTENSIONS):
                files.append(os.path.join(root, name))
    return files


def load_photo(path):
    try:
        return pygame.image.load(path).convert()
    except Exception as e:
        print(f"Could not load {path}: {e}")
        return None


def cover_image(image, size):
    target_w, target_h = size
    iw, ih = image.get_size()

    if iw <= 0 or ih <= 0:
        return pygame.Surface(size)

    scale = max(target_w / iw, target_h / ih)
    new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    scaled = pygame.transform.smoothscale(image, new_size)

    result = pygame.Surface(size, pygame.SRCALPHA)
    crop_x = max(0, (scaled.get_width() - target_w) // 2)
    crop_y = max(0, (scaled.get_height() - target_h) // 2)
    result.blit(scaled, (-crop_x, -crop_y))
    return result


# ------------------------- CARD ------------------------------
class Card:
    def __init__(self, pair_id, image):
        self.pair_id = pair_id
        self.image = image
        self.rect = pygame.Rect(0, 0, 100, 100)
        self.revealed = False
        self.matched = False
        self.flip_progress = 0.0
        self.flip_target = 0.0

    def set_revealed(self, value):
        self.revealed = value
        self.flip_target = 1.0 if value else 0.0

    def update(self, dt):
        speed = 1.0 / CARD_FLIP_TIME
        if self.flip_progress < self.flip_target:
            self.flip_progress = min(self.flip_target,
                                     self.flip_progress + speed * dt)
        elif self.flip_progress > self.flip_target:
            self.flip_progress = max(self.flip_target,
                                     self.flip_progress - speed * dt)

    def draw(self, surface):
        shadow = self.rect.copy()
        shadow.y += 7
        rounded_rect(surface, SHADOW, shadow, 18)

        progress = self.flip_progress
        scale_x = max(0.07, abs(math.cos(progress * math.pi)))
        draw_width = max(8, int(self.rect.width * scale_x))

        draw_rect = pygame.Rect(self.rect.centerx - draw_width // 2,
                                self.rect.y, draw_width, self.rect.height)

        if progress > 0.5:
            photo = cover_image(self.image, (draw_width, self.rect.height))

            mask = pygame.Surface((draw_width, self.rect.height),
                                  pygame.SRCALPHA)
            rounded_rect(mask, (255, 255, 255, 255), mask.get_rect(), 16)
            photo.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            surface.blit(photo, draw_rect)
            pygame.draw.rect(surface, WHITE, draw_rect, width=4,
                             border_radius=16)
        else:
            rounded_rect(surface, CARD_BLUE, draw_rect, 18)
            pygame.draw.rect(surface, WHITE, draw_rect, width=3,
                             border_radius=18)

            if draw_width > 45:
                star_r = max(8, int(self.rect.height * 0.09))
                draw_star(surface,
                          (draw_rect.x + draw_width * 0.25,
                           draw_rect.y + self.rect.height * 0.22),
                          star_r, (117, 191, 249))
                draw_star(surface,
                          (draw_rect.right - draw_width * 0.23,
                           draw_rect.bottom - self.rect.height * 0.22),
                          star_r, (117, 191, 249))

                q_font = font(max(30, int(self.rect.height * 0.48)), True)
                draw_text_center(surface, "?", q_font, WHITE,
                                 draw_rect.center)

        if self.matched and draw_width > 10:
            pygame.draw.rect(surface, GREEN, draw_rect, width=5,
                             border_radius=16)


# --------------------- GAME SETUP ----------------------------
def create_game():
    files = find_images()
    random.shuffle(files)

    if len(files) < MAX_PAIRS:
        return [], "NO_IMAGES"

    cards = []
    pair_id = 0
    for path in files:
        if pair_id == MAX_PAIRS:
            break
        image = load_photo(path)
        if image is None:
            continue
        cards.append(Card(pair_id, image))
        cards.append(Card(pair_id, image))
        pair_id += 1

    if len(cards) != TOTAL_CARDS:
        return [], "NO_IMAGES"

    random.shuffle(cards)
    return cards, None


# ---------------------- LAYOUT -------------------------------
def calculate_layout(width, height, card_count):
    title_rect = pygame.Rect(int(width * 0.22), int(height * 0.055),
                             int(width * 0.56), int(height * 0.135))

    home_size = int(min(width, height) * 0.12)
    home_rect = pygame.Rect(int(width * 0.025), int(height * 0.045),
                            home_size, home_size)

    score_rect = pygame.Rect(int(width * 0.835), int(height * 0.055),
                             int(width * 0.14), int(height * 0.075))

    cols = 4
    gap = max(7, int(min(width, height) * 0.012))
    grid_size = min(width * 0.68, height * 0.62)
    card_size = (grid_size - gap * (cols - 1)) / cols
    actual_grid_size = card_size * cols + gap * (cols - 1)
    grid_x = (width - actual_grid_size) / 2
    grid_y = height * 0.335

    card_rects = []
    for i in range(min(card_count, TOTAL_CARDS)):
        row = i // cols
        col = i % cols
        x = grid_x + col * (card_size + gap)
        y = grid_y + row * (card_size + gap)
        card_rects.append(pygame.Rect(round(x), round(y),
                                      round(card_size), round(card_size)))

    return title_rect, home_rect, score_rect, card_rects


def calculate_win_panel_rect(width, height):
    panel_width = min(int(width * 0.62), 650)
    panel_height = min(int(height * 0.43), 310)
    return pygame.Rect((width - panel_width) // 2,
                       (height - panel_height) // 2,
                       panel_width, panel_height)


def calculate_play_again_rect(width, height):
    panel = calculate_win_panel_rect(width, height)
    button_width = min(int(width * 0.28), 330)
    button_height = max(54, int(height * 0.085))
    button = pygame.Rect(0, 0, button_width, button_height)
    button.center = (width // 2, int(panel.y + panel.height * 0.76))
    return button


def calculate_start_rect(width, height):
    return pygame.Rect(int(width * 0.32), int(height * 0.55),
                       int(width * 0.36), int(height * 0.18))


# ------------------------- STATE ------------------------------
cards = []
game_state = "playing"

score = 0
pairs_found = 0

first_card = None
second_card = None

wrong_timer = 0.0
win_timer = 0.0

message = ""
message_timer = 0.0

game_won = False
home_error = ""
image_count = len(find_images())


def start_game():
    global cards, score, pairs_found
    global first_card, second_card
    global wrong_timer, win_timer
    global message, message_timer
    global game_won

    cards, error = create_game()

    score = 0
    pairs_found = 0
    first_card = None
    second_card = None
    wrong_timer = 0
    win_timer = 0
    message = ""
    message_timer = 0
    game_won = False

    return error is None

    


def go_home():
    global game_state, image_count, home_error
    game_state = "home"
    image_count = len(find_images())
    home_error = ""


def select_card(card):
    global first_card, second_card

    if card.matched or card.revealed:
        return
    if wrong_timer > 0:
        return

    if first_card is None:
        first_card = card
        card.set_revealed(True)
    elif second_card is None:
        second_card = card
        card.set_revealed(True)

    
# ------------------------- MAIN LOOP --------------------------
start_game()
game_state = "playing"
running = True

while running:
    dt = clock.tick(FPS) / 1000.0
    width, height = screen.get_size()

    # ---------------------- EVENTS ----------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                if game_state == "playing":
                    start_game()
            elif event.key == pygame.K_h:
                go_home()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse = event.pos

            if game_state == "home":
                if calculate_start_rect(width, height).collidepoint(mouse):
                    image_count = len(find_images())
                    if start_game():
                        game_state = "playing"
                        home_error = ""
                    else:
                        home_error = "Not enough photos. Add at least 8 to the 'pictures' folder."

            elif game_state == "playing":
                title_rect, home_rect, score_rect, card_rects = \
                    calculate_layout(width, height, len(cards))

                if game_won:
                    play_again_rect = calculate_play_again_rect(width, height)
                    if play_again_rect.collidepoint(mouse):
                        start_game()
                elif home_rect.collidepoint(mouse):
                    go_home()
                elif win_timer <= 0:
                    for card, rect in zip(cards, card_rects):
                        card.rect = rect
                        if rect.collidepoint(mouse):
                            select_card(card)
                            break

    # ---------------------- UPDATE ----------------------
    for card in cards:
        card.update(dt)

    if message_timer > 0:
        message_timer -= dt
        if message_timer <= 0:
            message = ""

    if wrong_timer > 0:
        wrong_timer -= dt
        if wrong_timer <= 0:
            if first_card:
                first_card.set_revealed(False)
            if second_card:
                second_card.set_revealed(False)
            first_card = None
            second_card = None

    if (first_card is not None
            and second_card is not None
            and wrong_timer <= 0
            and not first_card.matched
            and not second_card.matched):

        if first_card.pair_id == second_card.pair_id:
            first_card.matched = True
            second_card.matched = True

            score += 10
            pairs_found += 1

            first_card = None
            second_card = None

            message = "Great match!"
            message_timer = 1.0

            if pairs_found == MAX_PAIRS:
                win_timer = 1.2
        else:
            wrong_timer = WRONG_SHOW_TIME

    if win_timer > 0:
        win_timer -= dt
        if win_timer <= 0:
            game_won = True
            message = ""
            message_timer = 0

    # ----------------------- DRAW -----------------------
    draw_grid_background(screen)

    if game_state == "home":
        title_rect = pygame.Rect(int(width * 0.22), int(height * 0.12),
                                 int(width * 0.56), int(height * 0.16))
        draw_title(screen, title_rect)

        subtitle_font = font(max(22, min(34, int(width * 0.020))), True)
        draw_text_center(screen, "Find and match the pairs of pictures!",
                         subtitle_font, WHITE, (width / 2, height * 0.38))

        start_rect = calculate_start_rect(width, height)
        hovered = start_rect.collidepoint(pygame.mouse.get_pos())
        button_color = (139, 91, 245) if hovered else PURPLE

        shadow = start_rect.copy()
        shadow.y += 7
        rounded_rect(screen, SHADOW, shadow, 25)
        rounded_rect(screen, button_color, start_rect, 25)
        pygame.draw.rect(screen, (190, 153, 255), start_rect, width=3,
                         border_radius=25)

        start_font = font(max(25, min(42, int(width * 0.025))), True)
        draw_text_center(screen, "START PICTURE MATCHING", start_font,
                         WHITE, start_rect.center)

        small_font = font(max(16, int(width * 0.012)))
        draw_text_center(
            screen,
            f"{image_count} photos found in the 'pictures' folder (need at least 8)",
            small_font, (175, 194, 225), (width / 2, height * 0.80))
        draw_text_center(screen, "Add your own real photos to play!",
                         small_font, (175, 194, 225),
                         (width / 2, height * 0.85))

        if home_error:
            draw_text_center(screen, home_error, small_font,
                             (255, 120, 120), (width / 2, height * 0.91))

    else:
        title_rect, home_rect, score_rect, card_rects = \
            calculate_layout(width, height, len(cards))

        draw_home_button(screen, home_rect)
        draw_title(screen, title_rect)
        draw_score(screen, score_rect, score)

        subtitle_font = font(max(20, min(34, int(width * 0.020))), True)
        draw_text_center(screen, "Find and match all 8 pairs of pictures!",
                         subtitle_font, WHITE, (width / 2, height * 0.285))

        for card, rect in zip(cards, card_rects):
            card.rect = rect
            card.draw(screen)

        if game_won:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((2, 8, 25, 175))
            screen.blit(overlay, (0, 0))

            panel = calculate_win_panel_rect(width, height)
            panel_shadow = panel.copy()
            panel_shadow.y += 8
            rounded_rect(screen, SHADOW, panel_shadow, 30)
            rounded_rect(screen, (22, 55, 112), panel, 30)
            pygame.draw.rect(screen, (100, 174, 255), panel, width=4,
                             border_radius=30)

            win_font = font(max(28, min(48, int(width * 0.035))), True)
            draw_text_center(screen, "Amazing!", win_font, YELLOW,
                             (width / 2, panel.y + panel.height * 0.27))

            detail_font = font(max(18, min(29, int(width * 0.020))), True)
            draw_text_center(screen, "You matched all the pictures!",
                             detail_font, WHITE,
                             (width / 2, panel.y + panel.height * 0.48))

            play_again_rect = calculate_play_again_rect(width, height)
            hovered = play_again_rect.collidepoint(pygame.mouse.get_pos())
            button_color = (139, 91, 245) if hovered else PURPLE

            button_shadow = play_again_rect.copy()
            button_shadow.y += 5
            rounded_rect(screen, SHADOW, button_shadow, 18)
            rounded_rect(screen, button_color, play_again_rect, 18)
            pygame.draw.rect(screen, (190, 153, 255), play_again_rect,
                             width=3, border_radius=18)

            play_font = font(max(20, min(30, int(width * 0.021))), True)
            draw_text_center(screen, "PLAY AGAIN", play_font, WHITE,
                             play_again_rect.center)

        elif message:
            message_font = font(max(18, min(30, int(width * 0.018))), True)
            draw_text_center(screen, message, message_font, GREEN,
                             (width / 2, height * 0.95))

    pygame.display.flip()

pygame.quit()
sys.exit()