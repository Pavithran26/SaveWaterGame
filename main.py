import json
import random
from pathlib import Path

import pygame

from classes import (
    HEIGHT,
    TANK_HEIGHT,
    TANK_WIDTH,
    WATER_HEIGHT,
    WATER_WIDTH,
    Particle,
    PowerUp,
    RainDrop,
    Tank,
    Water,
)


BASE_DIR = Path(__file__).resolve().parent
WIDTH = 500
FPS = 60
HIGH_SCORE_FILE = BASE_DIR / "highscore.json"

# Visual language: deep storm navy, aqua water, and bright feedback accents.
NAVY = (7, 20, 36)
NAVY_LIGHT = (13, 39, 61)
BLUE = (42, 183, 235)
BLUE_LIGHT = (150, 231, 255)
WHITE = (245, 250, 252)
MUTED = (156, 188, 202)
GREEN = (91, 225, 145)
ORANGE = (255, 180, 78)
RED = (255, 101, 110)
PURPLE = (188, 130, 255)


class Game:
    def __init__(self):
        pygame.init()
        self.audio_enabled = self._init_audio()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Save Water | Storm Catcher")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("dejavusans", 34, bold=True)
        self.font_large = pygame.font.SysFont("dejavusans", 26, bold=True)
        self.font_body = pygame.font.SysFont("dejavusans", 18)
        self.font_small = pygame.font.SysFont("dejavusans", 14)
        self.font_tiny = pygame.font.SysFont("dejavusans", 11, bold=True)
        self.load_assets()
        self.high_score = self.load_high_score()
        self.rain = [RainDrop() for _ in range(62)]
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
                pygame.mixer.music.set_volume(0.22)
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
        self.powerups = []
        self.particles = []
        self.score = 0
        self.lives = 5
        self.combo = 0
        self.best_combo = 0
        self.level = 1
        self.spawn_timer = 0.0
        self.powerup_timer = 7.0
        self.total_time = 0.0
        self.banner = ""
        self.banner_timer = 0.0
        self.shield = 0

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
        return max(0.18, 0.82 - self.level * 0.045)

    def create_particles(self, position, color, amount=10):
        self.particles.extend(Particle(position[0], position[1], color) for _ in range(amount))

    def update_rain(self, dt):
        intensity = 1.0 + (self.level - 1) * 0.08 if self.state == "playing" else 0.65
        for streak in self.rain:
            streak.update(dt, intensity)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.tank.move(direction, dt)
        self.total_time += dt
        self.spawn_timer += dt
        self.powerup_timer -= dt
        self.banner_timer = max(0, self.banner_timer - dt)

        self.level = 1 + self.score // 10
        while self.spawn_timer >= self.spawn_interval():
            self.spawn_timer -= self.spawn_interval()
            self.waters.append(Water())
        if self.powerup_timer <= 0 and len(self.powerups) < 2:
            self.powerups.append(PowerUp())
            self.powerup_timer = random.uniform(11, 16)

        water_speed = 205 + min(self.level * 14, 160)
        for drop in self.waters[:]:
            drop.update(water_speed, dt)
            if drop.collides_with(self.tank):
                self.waters.remove(drop)
                self.combo += 1
                self.best_combo = max(self.best_combo, self.combo)
                multiplier = min(5, 1 + self.combo // 5)
                self.score += multiplier
                self.create_particles(drop.rect.center, BLUE_LIGHT, 12)
                self.play_sound(self.catch_sound)
                if self.combo % 5 == 0:
                    self.banner = f"COMBO x{multiplier}  +{multiplier}"
                    self.banner_timer = 1.25
            elif drop.missed():
                self.waters.remove(drop)
                if self.shield:
                    self.shield = 0
                    self.banner = "SHIELD SAVED THE DROP"
                    self.banner_timer = 1.1
                    self.create_particles((self.tank.rect.centerx, HEIGHT - 64), PURPLE, 14)
                else:
                    self.lives -= 1
                    self.combo = 0
                    self.create_particles((drop.rect.centerx, HEIGHT - 18), RED, 7)
                    self.play_sound(self.miss_sound)
                    if self.lives <= 0:
                        self.finish_round()
                        return

        for powerup in self.powerups[:]:
            powerup.update(145 + self.level * 8, dt)
            if powerup.collides_with(self.tank):
                self.powerups.remove(powerup)
                if powerup.kind == "shield":
                    self.shield = 1
                    self.banner = "SHIELD READY"
                    color = PURPLE
                else:
                    self.score += 5
                    self.banner = "BONUS DROP  +5"
                    color = ORANGE
                self.banner_timer = 1.2
                self.create_particles(powerup.rect.center, color, 18)
            elif powerup.missed():
                self.powerups.remove(powerup)

        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)

    def draw_text(self, text, font, color, center, surface=None):
        surface = surface or self.screen
        rendered = font.render(text, True, color)
        surface.blit(rendered, rendered.get_rect(center=center))

    def draw_background(self):
        self.screen.blit(self.background, (0, 0))
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((NAVY[0], NAVY[1], NAVY[2], 142))
        self.screen.blit(shade, (0, 0))
        rain_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for streak in self.rain:
            pygame.draw.line(
                rain_layer,
                (BLUE_LIGHT[0], BLUE_LIGHT[1], BLUE_LIGHT[2], streak.alpha),
                (streak.x, int(streak.y)),
                (streak.x - 3, int(streak.y + streak.length)),
                1,
            )
        self.screen.blit(rain_layer, (0, 0))

    def draw_heart(self, center, color, scale=1.0):
        x, y = center
        radius = max(3, round(5 * scale))
        pygame.draw.circle(self.screen, color, (x - radius // 2, y - radius // 3), radius)
        pygame.draw.circle(self.screen, color, (x + radius // 2, y - radius // 3), radius)
        pygame.draw.polygon(self.screen, color, [(x - radius * 1.45, y), (x + radius * 1.45, y), (x, y + radius * 1.8)])

    def draw_drop_icon(self, center, color=BLUE_LIGHT, scale=1.0):
        x, y = center
        radius = max(3, round(7 * scale))
        pygame.draw.circle(self.screen, color, (x, y + radius // 2), radius)
        pygame.draw.polygon(self.screen, color, [(x, y - radius * 1.65), (x - radius, y + 2), (x + radius, y + 2)])

    def draw_shield_icon(self, center, active=True):
        x, y = center
        color = PURPLE if active else MUTED
        points = [(x, y - 10), (x + 9, y - 5), (x + 7, y + 7), (x, y + 12), (x - 7, y + 7), (x - 9, y - 5)]
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.line(self.screen, NAVY, (x, y - 5), (x, y + 6), 2)
        pygame.draw.line(self.screen, NAVY, (x - 4, y), (x + 4, y), 2)

    def draw_hud(self):
        pygame.draw.rect(self.screen, (5, 17, 31), (0, 0, WIDTH, 68))
        pygame.draw.line(self.screen, BLUE, (0, 67), (WIDTH, 67), 2)
        self.screen.blit(self.font_tiny.render("SAVE WATER", True, BLUE_LIGHT), (17, 10))
        self.screen.blit(self.font_tiny.render(f"LEVEL {self.level}", True, ORANGE), (17, 31))
        self.draw_text(str(self.score), self.font_large, WHITE, (244, 24))
        self.draw_text("SCORE", self.font_tiny, MUTED, (244, 51))
        for index in range(5):
            self.draw_heart((366 + index * 18, 18), RED if index < self.lives else NAVY_LIGHT, 0.75)
        self.draw_text("LIVES", self.font_tiny, MUTED, (402, 48))
        if self.shield:
            self.draw_shield_icon((475, 22))
        pygame.draw.rect(self.screen, NAVY_LIGHT, (180, 59, 132, 4), border_radius=2)
        progress = (self.score % 10) / 10
        pygame.draw.rect(self.screen, BLUE, (180, 59, round(132 * progress), 4), border_radius=2)

    def draw_powerup(self, powerup):
        x, y = powerup.rect.centerx, powerup.rect.centery + powerup.bob_offset
        color = PURPLE if powerup.kind == "shield" else ORANGE
        pygame.draw.circle(self.screen, (8, 25, 43), (x, y), 18)
        pygame.draw.circle(self.screen, color, (x, y), 15, 2)
        if powerup.kind == "shield":
            self.draw_shield_icon((x, y), True)
        else:
            pygame.draw.polygon(self.screen, color, [(x + 2, y - 11), (x - 6, y + 1), (x - 1, y + 1), (x - 3, y + 11), (x + 7, y - 3), (x + 1, y - 3)])

    def draw_particles(self):
        for particle in self.particles:
            alpha = round(255 * min(1, particle.life / particle.max_life))
            layer = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(layer, (*particle.color, alpha), (5, 5), particle.radius)
            self.screen.blit(layer, (round(particle.x - 5), round(particle.y - 5)))

    def draw_playfield(self):
        self.draw_background()
        for drop in self.waters:
            self.screen.blit(self.water_image, drop.rect)
        for powerup in self.powerups:
            self.draw_powerup(powerup)
        self.draw_particles()
        shadow = pygame.Surface((TANK_WIDTH + 20, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 95), shadow.get_rect())
        self.screen.blit(shadow, (self.tank.rect.centerx - shadow.get_width() // 2, HEIGHT - 27))
        self.screen.blit(self.tank_image, self.tank.rect)
        self.draw_hud()
        if self.combo >= 2:
            self.draw_text(f"COMBO {self.combo}", self.font_small, GREEN, (WIDTH // 2, 88))
        if self.banner_timer > 0:
            self.draw_text(self.banner, self.font_body, ORANGE, (WIDTH // 2, 112))

    def draw_panel(self, height=250):
        panel = pygame.Surface((WIDTH - 56, height), pygame.SRCALPHA)
        panel.fill((5, 18, 32, 232))
        self.screen.blit(panel, (28, (HEIGHT - height) // 2))
        pygame.draw.rect(self.screen, BLUE, (28, (HEIGHT - height) // 2, WIDTH - 56, height), 2, border_radius=12)

    def draw_menu(self):
        self.draw_background()
        self.draw_panel(330)
        self.draw_drop_icon((WIDTH // 2, 77), BLUE_LIGHT, 1.4)
        self.draw_text("SAVE", self.font_title, WHITE, (WIDTH // 2, 120))
        self.draw_text("WATER", self.font_title, BLUE_LIGHT, (WIDTH // 2, 160))
        self.draw_text("STORM CATCHER", self.font_tiny, ORANGE, (WIDTH // 2, 194))
        pygame.draw.rect(self.screen, BLUE, (128, 222, 244, 52), border_radius=10)
        self.draw_text("PRESS ENTER TO PLAY", self.font_body, NAVY, (WIDTH // 2, 248))
        self.draw_text("←  →   Move tank", self.font_small, WHITE, (WIDTH // 2, 305))
        self.draw_text("Catch drops  •  Build combos  •  Grab power-ups", self.font_tiny, MUTED, (WIDTH // 2, 330))
        self.draw_text("P Pause     M Sound     ESC Quit", self.font_small, MUTED, (WIDTH // 2, 356))
        self.draw_text(f"BEST SCORE  {self.high_score}", self.font_small, GREEN, (WIDTH // 2, 388))

    def draw_pause(self):
        self.draw_playfield()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 14, 25, 175))
        self.screen.blit(overlay, (0, 0))
        self.draw_panel(190)
        self.draw_text("PAUSED", self.font_title, WHITE, (WIDTH // 2, 190))
        self.draw_text("Press P to continue", self.font_body, BLUE_LIGHT, (WIDTH // 2, 235))
        self.draw_text("ESC returns to menu", self.font_small, MUTED, (WIDTH // 2, 270))

    def draw_game_over(self):
        self.draw_background()
        self.draw_panel(300)
        self.draw_text("STORM COMPLETE", self.font_large, WHITE, (WIDTH // 2, 135))
        self.draw_drop_icon((WIDTH // 2, 178), BLUE_LIGHT, 1.0)
        self.draw_text(f"{self.score}", self.font_title, BLUE_LIGHT, (WIDTH // 2, 220))
        self.draw_text(f"SCORE  •  LEVEL {self.level}  •  BEST COMBO {self.best_combo}", self.font_tiny, MUTED, (WIDTH // 2, 250))
        best_color = GREEN if self.score >= self.high_score else MUTED
        self.draw_text(f"Best score  {self.high_score}", self.font_body, best_color, (WIDTH // 2, 282))
        self.draw_text("Press R to play again", self.font_body, WHITE, (WIDTH // 2, 325))
        self.draw_text("ESC returns to menu", self.font_small, MUTED, (WIDTH // 2, 355))

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
            self.update_rain(dt)
            if running and self.state == "playing":
                self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
