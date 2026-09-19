import json
from pathlib import Path

import pygame

from classes import HEIGHT, TANK_HEIGHT, TANK_WIDTH, WATER_HEIGHT, WATER_WIDTH, Tank, Water


BASE_DIR = Path(__file__).resolve().parent
WIDTH = 500
FPS = 60
HIGH_SCORE_FILE = BASE_DIR / "highscore.json"

# Color system: deep navy canvas with water-blue action color and warm alerts.
NAVY = (8, 22, 38)
NAVY_LIGHT = (14, 40, 62)
BLUE = (46, 176, 232)
BLUE_LIGHT = (145, 224, 255)
WHITE = (245, 250, 252)
MUTED = (160, 190, 202)
GREEN = (91, 220, 145)
ORANGE = (255, 177, 78)
RED = (255, 102, 102)


class Game:
    def __init__(self):
        pygame.init()
        self.audio_enabled = self._init_audio()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Save Water | Catch Every Drop")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("dejavusans", 34, bold=True)
        self.font_large = pygame.font.SysFont("dejavusans", 26, bold=True)
        self.font_body = pygame.font.SysFont("dejavusans", 18)
        self.font_small = pygame.font.SysFont("dejavusans", 14)
        self.load_assets()
        self.high_score = self.load_high_score()
        self.state = "menu"
        self.reset_round()

    def _init_audio(self):
        try:
            pygame.mixer.init()
            return True
        except pygame.error:
            return False

    def load_assets(self):
        def image(name, size):
            loaded = pygame.image.load(BASE_DIR / name).convert_alpha()
            return pygame.transform.smoothscale(loaded, size)

        self.background = pygame.transform.smoothscale(
            pygame.image.load(BASE_DIR / "background.jpg").convert(), (WIDTH, HEIGHT)
        )
        self.water_image = image("water.png", (WATER_WIDTH, WATER_HEIGHT))
        self.tank_image = image("tank.png", (TANK_WIDTH, TANK_HEIGHT))
        self.catch_sound = self.load_sound("point_sound.mp3")
        self.miss_sound = self.load_sound("water_sound.mp3")
        if self.audio_enabled:
            try:
                pygame.mixer.music.load(BASE_DIR / "background.mp3")
                pygame.mixer.music.set_volume(0.25)
            except pygame.error:
                self.audio_enabled = False

    @staticmethod
    def load_sound(name):
        try:
            return pygame.mixer.Sound(BASE_DIR / name)
        except pygame.error:
            return None

    @staticmethod
    def load_high_score():
        try:
            return int(json.loads(HIGH_SCORE_FILE.read_text()).get("high_score", 0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return 0

    def save_high_score(self):
        try:
            HIGH_SCORE_FILE.write_text(json.dumps({"high_score": self.high_score}))
        except OSError:
            pass

    def reset_round(self):
        self.tank = Tank()
        self.waters = []
        self.score = 0
        self.lives = 5
        self.spawn_timer = 0.0
        self.total_time = 0.0

    def start_round(self):
        self.reset_round()
        self.state = "playing"
        if self.audio_enabled:
            try:
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass

    def finish_round(self):
        self.state = "game_over"
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def play_sound(self, sound):
        if self.audio_enabled and sound:
            sound.play()

    def spawn_interval(self):
        # Difficulty increases smoothly but never becomes overwhelming.
        return max(0.22, 0.95 - self.score * 0.012)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.tank.move(direction, dt)
        self.total_time += dt
        self.spawn_timer += dt
        while self.spawn_timer >= self.spawn_interval():
            self.spawn_timer -= self.spawn_interval()
            self.waters.append(Water())

        # Iterate over a copy so removing a caught/missed drop cannot skip another drop.
        for drop in self.waters[:]:
            drop.update(210 + min(self.score * 3, 130), dt)
            if drop.collides_with(self.tank):
                self.waters.remove(drop)
                self.score += 1
                self.play_sound(self.catch_sound)
            elif drop.missed():
                self.waters.remove(drop)
                self.lives -= 1
                self.play_sound(self.miss_sound)
                if self.lives <= 0:
                    self.finish_round()
                    return

    def draw_text(self, text, font, color, center, surface=None):
        surface = surface or self.screen
        rendered = font.render(text, True, color)
        surface.blit(rendered, rendered.get_rect(center=center))

    def draw_background(self):
        self.screen.blit(self.background, (0, 0))
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((NAVY[0], NAVY[1], NAVY[2], 135))
        self.screen.blit(shade, (0, 0))

    def draw_hud(self):
        pygame.draw.rect(self.screen, NAVY, (0, 0, WIDTH, 58))
        self.screen.blit(self.font_small.render("SAVE WATER", True, BLUE_LIGHT), (18, 10))
        self.screen.blit(self.font_small.render("CATCH THE DROPS", True, MUTED), (18, 31))
        score = self.font_large.render(f"{self.score:02d}", True, WHITE)
        self.screen.blit(score, (220, 13))
        self.draw_text("SCORE", self.font_small, MUTED, (250, 14))
        self.draw_text(f"LIVES  {'●' * self.lives}", self.font_small, RED, (410, 20))

    def draw_playfield(self):
        self.draw_background()
        for drop in self.waters:
            self.screen.blit(self.water_image, drop.rect)
        self.screen.blit(self.tank_image, self.tank.rect)
        self.draw_hud()

    def draw_panel(self, height=250):
        panel = pygame.Surface((WIDTH - 56, height), pygame.SRCALPHA)
        panel.fill((5, 18, 32, 225))
        self.screen.blit(panel, (28, (HEIGHT - height) // 2))
        pygame.draw.rect(self.screen, BLUE, (28, (HEIGHT - height) // 2, WIDTH - 56, height), 2, border_radius=12)

    def draw_menu(self):
        self.draw_background()
        self.draw_panel(300)
        self.draw_text("SAVE", self.font_title, WHITE, (WIDTH // 2, 120))
        self.draw_text("WATER", self.font_title, BLUE_LIGHT, (WIDTH // 2, 160))
        self.draw_text("Every drop counts.", self.font_body, MUTED, (WIDTH // 2, 199))
        pygame.draw.rect(self.screen, BLUE, (128, 229, 244, 52), border_radius=10)
        self.draw_text("PRESS ENTER TO PLAY", self.font_body, NAVY, (WIDTH // 2, 255))
        self.draw_text("←  →   Move tank", self.font_small, WHITE, (WIDTH // 2, 310))
        self.draw_text("P   Pause     M   Sound     ESC   Quit", self.font_small, MUTED, (WIDTH // 2, 337))
        self.draw_text(f"Best score: {self.high_score}", self.font_small, GREEN, (WIDTH // 2, 370))

    def draw_pause(self):
        self.draw_playfield()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 14, 25, 170))
        self.screen.blit(overlay, (0, 0))
        self.draw_panel(190)
        self.draw_text("PAUSED", self.font_title, WHITE, (WIDTH // 2, 190))
        self.draw_text("Press P to continue", self.font_body, BLUE_LIGHT, (WIDTH // 2, 235))
        self.draw_text("Press ESC to return to menu", self.font_small, MUTED, (WIDTH // 2, 270))

    def draw_game_over(self):
        self.draw_background()
        self.draw_panel(280)
        self.draw_text("ROUND COMPLETE", self.font_large, WHITE, (WIDTH // 2, 145))
        self.draw_text(f"Score  {self.score}", self.font_title, BLUE_LIGHT, (WIDTH // 2, 195))
        best_color = GREEN if self.score >= self.high_score else MUTED
        self.draw_text(f"Best score  {self.high_score}", self.font_body, best_color, (WIDTH // 2, 235))
        self.draw_text("Press R to play again", self.font_body, WHITE, (WIDTH // 2, 285))
        self.draw_text("Press ESC to return to menu", self.font_small, MUTED, (WIDTH // 2, 320))

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_playfield()
        elif self.state == "paused":
            self.draw_pause()
        else:
            self.draw_game_over()
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type != pygame.KEYDOWN:
            return True
        if event.key == pygame.K_ESCAPE:
            if self.state == "menu":
                return False
            self.state = "menu"
            if self.audio_enabled:
                pygame.mixer.music.stop()
        elif self.state == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.start_round()
        elif self.state == "playing" and event.key == pygame.K_p:
            self.state = "paused"
        elif self.state == "paused" and event.key == pygame.K_p:
            self.state = "playing"
        elif self.state == "game_over" and event.key == pygame.K_r:
            self.start_round()
        elif event.key == pygame.K_m:
            self.audio_enabled = not self.audio_enabled
            if self.audio_enabled:
                try:
                    pygame.mixer.music.play(-1)
                except pygame.error:
                    pass
            else:
                pygame.mixer.stop()
        return True

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                running = self.handle_event(event)
            if running and self.state == "playing":
                self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
