"""
What Is This?  -  a simple object-recognition mini-game for Memory Garden.

Play on its own:
    python what_is_this.py

Use inside the main Memory Garden app:
    from what_is_this import WhatIsThisGame

    game = WhatIsThisGame(screen)   # screen = the app's existing 1280x720 Pygame window
    result = game.run()             # the game runs here until the player leaves
    # result is "menu" (player chose Back to Menu / pressed Esc) or "quit" (window closed)
    # The game never calls pygame.quit(), so your app keeps running.
"""
import math
import os
import random
import sys

import pygame

WIDTH, HEIGHT = 1280, 720
PICTURE_SIZE = (340, 280)
IMAGE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")

# Colours
BACKGROUND, WHITE, DARK = (253, 247, 235), (255, 255, 255), (40, 50, 65)
GREEN, BLUE, GREY = (46, 125, 50), (30, 100, 170), (90, 100, 115)
LIGHT_BLUE, LIGHT_AMBER = (210, 230, 250), (255, 224, 160)

INSTRUCTION_LINES = ["Look at the picture", "and choose the correct answer."]

# ---------------------------------------------------------------------------
# QUESTIONS - to add one, add a line here and a PNG (or a draw function below).
# "answer" is also the picture name: assets/images/<answer in lowercase>.png
# ---------------------------------------------------------------------------
QUESTIONS = [
    {"answer": "Apple",    "wrong": ["Chair", "House"]},
    {"answer": "Banana",   "wrong": ["Cup", "Dog"]},
    {"answer": "Chair",    "wrong": ["Apple", "Clock"]},
    {"answer": "Cup",      "wrong": ["Cat", "Book"]},
    {"answer": "House",    "wrong": ["Banana", "Spoon"]},
    {"answer": "Clock",    "wrong": ["Flower", "Shoes"]},
    {"answer": "Dog",      "wrong": ["Car", "Umbrella"]},
    {"answer": "Cat",      "wrong": ["Bicycle", "Apple"]},
    {"answer": "Bicycle",  "wrong": ["Cup", "House"]},
    {"answer": "Book",     "wrong": ["Dog", "Chair"]},
    {"answer": "Flower",   "wrong": ["Clock", "Spoon"]},
    {"answer": "Car",      "wrong": ["Banana", "Cat"]},
    {"answer": "Spoon",    "wrong": ["Umbrella", "Book"]},
    {"answer": "Shoes",    "wrong": ["Flower", "Car"]},
    {"answer": "Umbrella", "wrong": ["Cup", "Bicycle"]},
]


# ---------------------------------------------------------------------------
# PICTURES DRAWN WITH PYGAME SHAPES (used when there is no PNG file).
# Each function draws on a white 340 x 280 surface called s.
# You can delete this whole section if you supply a PNG for every question.
# ---------------------------------------------------------------------------
def draw_apple(s):
    pygame.draw.circle(s, (210, 40, 40), (135, 160), 80)
    pygame.draw.circle(s, (210, 40, 40), (205, 160), 80)
    pygame.draw.line(s, (110, 70, 40), (170, 95), (178, 45), 10)           # stem
    pygame.draw.ellipse(s, (60, 160, 70), (180, 38, 70, 34))               # leaf
    pygame.draw.circle(s, (240, 130, 130), (115, 135), 14)                 # shine


def draw_banana(s):
    pygame.draw.arc(s, (250, 215, 40), (30, 0, 280, 250), 3.4, 6.0, 48)    # the curved body
    pygame.draw.circle(s, (120, 85, 40), (50, 168), 12)                    # tips
    pygame.draw.circle(s, (120, 85, 40), (296, 158), 12)


def draw_chair(s):
    wood = (160, 105, 60)
    pygame.draw.rect(s, wood, (90, 30, 20, 130))                           # back posts
    pygame.draw.rect(s, wood, (230, 30, 20, 130))
    pygame.draw.rect(s, wood, (90, 30, 160, 18))                           # back rails
    pygame.draw.rect(s, wood, (90, 75, 160, 14))
    pygame.draw.rect(s, (205, 145, 85), (80, 140, 180, 30), border_radius=8)   # seat
    pygame.draw.rect(s, wood, (95, 170, 20, 90))                           # front legs
    pygame.draw.rect(s, wood, (225, 170, 20, 90))


def draw_cup(s):
    blue = (70, 130, 210)
    pygame.draw.circle(s, blue, (245, 145), 38, 14)                        # handle
    pygame.draw.ellipse(s, (225, 230, 236), (60, 205, 210, 40))            # saucer
    pygame.draw.rect(s, blue, (90, 90, 150, 130), border_bottom_left_radius=60, border_bottom_right_radius=60)
    pygame.draw.ellipse(s, (50, 100, 180), (90, 78, 150, 28))              # rim
    pygame.draw.ellipse(s, (120, 70, 40), (100, 83, 130, 18))              # tea


def draw_house(s):
    pygame.draw.rect(s, (130, 90, 60), (225, 45, 26, 60))                  # chimney
    pygame.draw.rect(s, (240, 215, 170), (70, 120, 200, 130))              # walls
    pygame.draw.polygon(s, (190, 70, 60), [(50, 125), (170, 35), (290, 125)])   # roof
    pygame.draw.rect(s, (150, 100, 60), (145, 175, 50, 75))                # door
    for x in (88, 222):                                                    # two windows
        pygame.draw.rect(s, (150, 210, 245), (x, 150, 40, 40))
        pygame.draw.rect(s, WHITE, (x, 150, 40, 40), 3)


def draw_clock(s):
    center = (170, 140)
    pygame.draw.circle(s, (60, 60, 70), center, 118)                       # frame
    pygame.draw.circle(s, WHITE, center, 105)                              # face
    for hour in range(12):                                                 # 12 tick marks
        angle = math.radians(hour * 30)
        start = (center[0] + 82 * math.sin(angle), center[1] - 82 * math.cos(angle))
        end = (center[0] + 98 * math.sin(angle), center[1] - 98 * math.cos(angle))
        pygame.draw.line(s, DARK, start, end, 6)
    pygame.draw.line(s, DARK, center, (center[0] - 48, center[1] - 28), 10)   # hour hand
    pygame.draw.line(s, DARK, center, (center[0] + 69, center[1] - 40), 6)    # minute hand
    pygame.draw.circle(s, DARK, center, 9)


def draw_dog(s):
    pygame.draw.ellipse(s, (110, 65, 30), (60, 50, 60, 120))               # ears
    pygame.draw.ellipse(s, (110, 65, 30), (220, 50, 60, 120))
    pygame.draw.circle(s, (170, 110, 60), (170, 140), 82)                  # head
    pygame.draw.ellipse(s, (235, 205, 165), (125, 145, 90, 75))            # muzzle
    pygame.draw.ellipse(s, (30, 30, 30), (150, 150, 40, 28))               # nose
    pygame.draw.ellipse(s, (240, 110, 130), (158, 195, 24, 36))            # tongue
    pygame.draw.circle(s, (30, 30, 30), (138, 112), 10)                    # eyes
    pygame.draw.circle(s, (30, 30, 30), (202, 112), 10)


def draw_cat(s):
    orange = (235, 150, 60)
    pygame.draw.polygon(s, orange, [(75, 35), (75, 135), (150, 85)])       # ears
    pygame.draw.polygon(s, orange, [(265, 35), (265, 135), (190, 85)])
    pygame.draw.circle(s, orange, (170, 150), 88)                          # head
    for x in (125, 181):                                                   # eyes
        pygame.draw.ellipse(s, (120, 200, 90), (x, 120, 34, 40))
        pygame.draw.ellipse(s, (30, 30, 30), (x + 13, 125, 8, 30))
    pygame.draw.polygon(s, (240, 120, 140), [(160, 168), (180, 168), (170, 180)])   # nose
    for y in (172, 184):                                                   # whiskers
        pygame.draw.line(s, DARK, (115, y), (45, y - 12 + (y - 172)), 3)
        pygame.draw.line(s, DARK, (225, y), (295, y - 12 + (y - 172)), 3)


def draw_bicycle(s):
    rear, front, pedal, seat, bars = (80, 190), (260, 190), (165, 195), (135, 110), (225, 105)
    pygame.draw.circle(s, DARK, rear, 62, 8)                               # wheels
    pygame.draw.circle(s, DARK, front, 62, 8)
    for start, end in [(rear, pedal), (rear, seat), (pedal, seat), (seat, bars), (pedal, bars), (bars, front)]:
        pygame.draw.line(s, (200, 50, 50), start, end, 8)                  # red frame
    pygame.draw.line(s, DARK, (115, 100), (155, 100), 10)                  # seat
    pygame.draw.line(s, DARK, (225, 105), (225, 85), 8)                    # handlebars
    pygame.draw.line(s, DARK, (205, 85), (250, 85), 8)


def draw_book(s):
    pygame.draw.rect(s, WHITE, (102, 52, 160, 190), border_radius=8)       # pages
    pygame.draw.rect(s, (150, 155, 165), (102, 52, 160, 190), 3, border_radius=8)
    pygame.draw.rect(s, BLUE, (80, 40, 160, 190), border_radius=8)         # cover
    pygame.draw.rect(s, (20, 70, 130), (80, 40, 24, 190), border_radius=8) # spine
    pygame.draw.rect(s, WHITE, (125, 80, 95, 14), border_radius=6)         # title lines
    pygame.draw.rect(s, WHITE, (125, 108, 65, 10), border_radius=5)


def draw_flower(s):
    pygame.draw.line(s, (60, 150, 70), (170, 150), (170, 265), 10)         # stem
    pygame.draw.ellipse(s, (60, 160, 70), (176, 200, 70, 30))              # leaves
    pygame.draw.ellipse(s, (60, 160, 70), (94, 185, 70, 30))
    for dx, dy in [(0, -52), (45, -26), (45, 26), (0, 52), (-45, 26), (-45, -26)]:
        pygame.draw.circle(s, (235, 100, 150), (170 + dx, 100 + dy), 32)   # six petals
    pygame.draw.circle(s, (255, 205, 50), (170, 100), 30)                  # centre


def draw_car(s):
    red = (200, 50, 50)
    pygame.draw.polygon(s, red, [(110, 150), (140, 95), (230, 95), (255, 150)])   # roof
    pygame.draw.polygon(s, (170, 215, 245), [(125, 148), (148, 105), (168, 105), (168, 148)])   # windows
    pygame.draw.polygon(s, (170, 215, 245), [(178, 148), (178, 105), (225, 105), (243, 148)])
    pygame.draw.rect(s, red, (60, 150, 230, 60), border_radius=18)         # body
    pygame.draw.circle(s, (255, 230, 120), (280, 172), 8)                  # headlight
    for x in (115, 235):                                                   # wheels
        pygame.draw.circle(s, (40, 40, 50), (x, 212), 30)
        pygame.draw.circle(s, (190, 190, 200), (x, 212), 13)


def draw_spoon(s):
    silver = (190, 195, 205)
    pygame.draw.line(s, silver, (170, 140), (170, 255), 22)                # handle
    pygame.draw.circle(s, silver, (170, 255), 11)
    pygame.draw.ellipse(s, silver, (110, 20, 120, 160))                    # bowl
    pygame.draw.ellipse(s, (140, 145, 155), (110, 20, 120, 160), 5)
    pygame.draw.ellipse(s, (230, 235, 242), (132, 42, 30, 60))             # shine


def draw_one_shoe(s, x, y):
    pygame.draw.polygon(s, BLUE, [(x, y), (x + 70, y), (x + 80, y + 30), (x + 170, y + 55), (x + 180, y + 75), (x, y + 75)])
    pygame.draw.rect(s, DARK, (x, y + 66, 182, 14), border_radius=7)       # sole
    for i in range(3):                                                     # laces
        pygame.draw.line(s, WHITE, (x + 30 + i * 12, y + 8 + i * 5), (x + 50 + i * 12, y + 22 + i * 5), 4)


def draw_shoes(s):
    draw_one_shoe(s, 55, 45)                                               # a pair of shoes
    draw_one_shoe(s, 100, 150)


def draw_umbrella(s):
    pygame.draw.ellipse(s, (210, 60, 90), (40, 30, 260, 210))              # canopy: top half of an oval
    pygame.draw.rect(s, WHITE, (0, 135, 340, 145))                         # hide the bottom half
    for x in (85, 127, 213, 255):                                          # ribs
        pygame.draw.line(s, (150, 30, 60), (170, 32), (x, 130), 3)
    pygame.draw.line(s, DARK, (170, 135), (170, 240), 8)                   # pole
    pygame.draw.arc(s, DARK, (110, 215, 60, 50), math.pi, 2 * math.pi, 8)  # hook


# Links each answer name to its drawing function
DRAWINGS = {"Apple": draw_apple, "Banana": draw_banana, "Chair": draw_chair, "Cup": draw_cup,
            "House": draw_house, "Clock": draw_clock, "Dog": draw_dog, "Cat": draw_cat,
            "Bicycle": draw_bicycle, "Book": draw_book, "Flower": draw_flower, "Car": draw_car,
            "Spoon": draw_spoon, "Shoes": draw_shoes, "Umbrella": draw_umbrella}


# ---------------------------------------------------------------------------
# SMALL HELPERS
# ---------------------------------------------------------------------------
def load_picture(name):
    """Return the picture for an object: its PNG if there is one, otherwise the Pygame drawing."""
    picture = pygame.Surface(PICTURE_SIZE)
    picture.fill(WHITE)
    try:
        image = pygame.image.load(os.path.join(IMAGE_FOLDER, name.lower() + ".png")).convert_alpha()
        scale = min(PICTURE_SIZE[0] / image.get_width(), PICTURE_SIZE[1] / image.get_height())
        image = pygame.transform.smoothscale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
        picture.blit(image, image.get_rect(center=picture.get_rect().center))
    except (pygame.error, FileNotFoundError):         # no PNG found, so draw the shapes instead
        if name in DRAWINGS:
            DRAWINGS[name](picture)
    return picture


def draw_text(screen, text, font, color, center):
    image = font.render(text, True, color)
    screen.blit(image, image.get_rect(center=center))


def draw_button(screen, rect, text, color, text_color, font):
    pygame.draw.rect(screen, color, rect, border_radius=24)
    pygame.draw.rect(screen, DARK, rect, 3, border_radius=24)
    draw_text(screen, text, font, text_color, rect.center)


# ---------------------------------------------------------------------------
# THE GAME
# ---------------------------------------------------------------------------
class WhatIsThisGame:
    def __init__(self, screen=None):
        pygame.font.init()
        if screen is None:                            # started on its own, so make a window
            pygame.init()
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("What Is This?")
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("arial", 100, bold=True)
        self.big_font = pygame.font.SysFont("arial", 56, bold=True)
        self.medium_font = pygame.font.SysFont("arial", 44, bold=True)
        self.small_font = pygame.font.SysFont("arial", 28, bold=True)

        # Button positions (used both for drawing and for click detection)
        self.start_button = pygame.Rect(420, 450, 440, 120)
        self.help_button = pygame.Rect(900, 15, 340, 56)
        self.answer_buttons = [pygame.Rect(60 + i * 400, 450, 360, 85) for i in range(3)]
        self.next_button = pygame.Rect(440, 610, 400, 80)
        self.play_again_button = pygame.Rect(220, 480, 400, 100)
        self.menu_button = pygame.Rect(660, 480, 400, 100)

        # Game state
        self.state = "welcome"            # "welcome", "question" or "done"
        self.show_help = False            # True while the instructions pop-up is open
        self.order = []                   # question numbers in random order for this playthrough
        self.question_number = 0          # position in self.order (0 = first question)
        self.correct_count = 0
        self.right_answer = ""
        self.choices = []                 # the three answer texts, shuffled
        self.picture = None
        self.picked = None                # which answer button was clicked last (0, 1 or 2)
        self.solved = False               # True once the right answer has been chosen
        self.message = ""
        self.running = False
        self.result = "menu"

    # ----- game logic -----
    def start_game(self):
        self.order = list(range(len(QUESTIONS)))
        random.shuffle(self.order)        # every question appears exactly once, in random order
        self.question_number = 0
        self.correct_count = 0
        self.state = "question"
        self.load_question()

    def load_question(self):
        question = QUESTIONS[self.order[self.question_number]]
        self.right_answer = question["answer"]
        self.choices = [question["answer"]] + question["wrong"]
        random.shuffle(self.choices)      # the right answer lands in a random position
        self.picture = load_picture(question["answer"])
        self.picked, self.solved, self.message = None, False, ""

    def check_answer(self, button_number):
        if self.solved:                   # already correct, nothing more to choose
            return
        self.picked = button_number
        if self.choices[button_number] == self.right_answer:
            self.solved = True
            self.correct_count += 1
            self.message = "Wonderful! That's correct!"
        else:
            self.message = "Good try! Let's try again."   # no penalty, try as often as needed

    def next_question(self):
        self.question_number += 1
        if self.question_number >= len(QUESTIONS):
            self.state = "done"
        else:
            self.load_question()

    def handle_click(self, pos):
        if self.show_help:                # any click closes the instructions
            self.show_help = False
        elif self.state == "welcome":
            if self.start_button.collidepoint(pos):
                self.start_game()
        elif self.state == "question":
            if self.help_button.collidepoint(pos):
                self.show_help = True
            elif self.solved and self.next_button.collidepoint(pos):
                self.next_question()
            else:
                for number, button in enumerate(self.answer_buttons):
                    if button.collidepoint(pos):
                        self.check_answer(number)
        elif self.state == "done":
            if self.play_again_button.collidepoint(pos):
                self.start_game()
            elif self.menu_button.collidepoint(pos):
                self.running = False      # return to the main application

    # ----- drawing -----
    def draw_welcome(self):
        draw_text(self.screen, "What Is This?", self.title_font, GREEN, (WIDTH // 2, 140))
        for i, line in enumerate(INSTRUCTION_LINES):
            draw_text(self.screen, line, self.medium_font, DARK, (WIDTH // 2, 280 + i * 55))
        draw_button(self.screen, self.start_button, "Start Game", GREEN, WHITE, self.big_font)

    def draw_question(self):
        counter = f"Question {self.question_number + 1} of {len(QUESTIONS)}"
        self.screen.blit(self.small_font.render(counter, True, DARK), (40, 28))
        draw_button(self.screen, self.help_button, "Replay Instructions", GREY, WHITE, self.small_font)
        draw_text(self.screen, "What is this?", self.big_font, DARK, (WIDTH // 2, 85))

        frame = pygame.Rect(455, 115, 370, 310)       # white frame around the picture
        pygame.draw.rect(self.screen, WHITE, frame, border_radius=25)
        pygame.draw.rect(self.screen, (190, 195, 200), frame, 3, border_radius=25)
        self.screen.blit(self.picture, (frame.x + 15, frame.y + 15))

        for number, button in enumerate(self.answer_buttons):
            color, text_color = LIGHT_BLUE, DARK
            if number == self.picked and self.solved:
                color, text_color = GREEN, WHITE          # correct answer turns green
            elif number == self.picked:
                color = LIGHT_AMBER                       # a gentle highlight for a wrong try
            draw_button(self.screen, button, self.choices[number], color, text_color, self.medium_font)

        draw_text(self.screen, self.message, self.medium_font, GREEN if self.solved else DARK, (WIDTH // 2, 575))
        if self.solved:
            draw_button(self.screen, self.next_button, "Next Question", BLUE, WHITE, self.medium_font)

    def draw_done(self):
        draw_text(self.screen, "Well Done! You completed the game!", self.big_font, GREEN, (WIDTH // 2, 200))
        score = f"Correct answers: {self.correct_count} out of {len(QUESTIONS)}"
        draw_text(self.screen, score, self.medium_font, DARK, (WIDTH // 2, 320))
        draw_button(self.screen, self.play_again_button, "Play Again", GREEN, WHITE, self.big_font)
        draw_button(self.screen, self.menu_button, "Back to Menu", BLUE, WHITE, self.big_font)

    def draw_help(self):
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)   # dim the screen behind the pop-up
        veil.fill((30, 40, 50, 170))
        self.screen.blit(veil, (0, 0))
        panel = pygame.Rect(240, 190, 800, 340)
        pygame.draw.rect(self.screen, WHITE, panel, border_radius=30)
        draw_text(self.screen, "How to play", self.big_font, GREEN, (WIDTH // 2, 250))
        for i, line in enumerate(INSTRUCTION_LINES):
            draw_text(self.screen, line, self.medium_font, DARK, (WIDTH // 2, 340 + i * 55))
        draw_text(self.screen, "Click anywhere to continue.", self.small_font, GREY, (WIDTH // 2, 480))

    def draw(self):
        self.screen.fill(BACKGROUND)
        if self.state == "welcome":
            self.draw_welcome()
        elif self.state == "question":
            self.draw_question()
        else:
            self.draw_done()
        if self.show_help:
            self.draw_help()
        pygame.display.flip()

    # ----- main loop -----
    def run(self):
        """Play until the player leaves. Returns "menu" or "quit"."""
        self.state, self.show_help = "welcome", False
        self.running, self.result = True, "menu"
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:             # window closed
                    self.result, self.running = "quit", False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False                  # Esc = back to the menu
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
            self.draw()
            self.clock.tick(30)
        return self.result


if __name__ == "__main__":
    WhatIsThisGame().run()
    pygame.quit()
    sys.exit()
