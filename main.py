import json
import math
import random
from pathlib import Path

import pygame

from classes import (
    HEIGHT,
    TANK_HEIGHT,
    TANK_WIDTH,
    WATER_HEIGHT,
    WATER_WIDTH,
    Obstacle,
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
TOXIC = (184, 230, 76)
GOLD = (255, 215, 90)

MODES = (
    {"name": "RELAXED", "lives": 6, "speed": 0.84, "description": "More lives • gentle storm"},
    {"name": "STANDARD", "lives": 5, "speed": 1.0, "description": "Balanced challenge"},
    {"name": "CHALLENGE", "lives": 4, "speed": 1.18, "description": "Fast storm • toxic waste"},
)
TIPS = (
    "Turn off the tap while brushing your teeth.",
    "Fix leaking taps early to save water every day.",
    "Reuse water from washing vegetables for plants.",
    "Shorter showers can save many litres of water.",
    "Collect rainwater for your garden when possible.",
)
WORLDS = (
    {"name": "CALM DRIZZLE", "tint": (18, 37, 58), "rain": 0.72, "accent": BLUE_LIGHT, "event": "A calm cloudburst begins"},
    {"name": "RAINY AFTERNOON", "tint": (12, 31, 52), "rain": 1.0, "accent": BLUE, "event": "The rain is picking up"},
    {"name": "THUNDERSTORM", "tint": (22, 20, 52), "rain": 1.32, "accent": PURPLE, "event": "Thunder rolls across the sky"},
    {"name": "MONSOON SURGE", "tint": (26, 18, 42), "rain": 1.65, "accent": GOLD, "event": "The monsoon surge is here"},
)
DROP_LABELS = {"normal": "+1", "gold": "GOLD DROP  +3", "rainbow": "RAINBOW DROP  +5"}


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
        self.mode_index = 1
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

    @property
    def mode(self):
        return MODES[self.mode_index]

    @property
    def world(self):
        return WORLDS[min((self.level - 1) // 2, len(WORLDS) - 1)]

    def reset_round(self):
        self.tank = Tank(speed=320 * self.mode["speed"])
        self.waters = []
        self.obstacles = []
        self.powerups = []
        self.particles = []
        self.score = 0
        self.lives = self.mode["lives"]
        self.combo = 0
        self.best_combo = 0
        self.drops_caught = 0
        self.mission_target = 15
        self.mission_claimed = False
        self.level = 1
        self.spawn_timer = 0.0
        self.obstacle_timer = 0.0
        self.powerup_timer = 7.0
        self.total_time = 0.0
        self.banner = ""
        self.banner_timer = 0.0
        self.shield = 0
        self.end_tip = random.choice(TIPS)
        self.completed_milestones = set()
        self.celebration_milestone = 0
        self.celebration_timer = 0.0
        self.celebration_kind = "milestone"
        self.thunder_timer = random.uniform(4.0, 8.0)
        self.lightning_flash = 0.0
        self.world_banner = self.world["event"]
        self.world_banner_timer = 2.0
        self.last_world_name = self.world["name"]

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
        self.end_tip = random.choice(TIPS)
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def add_score(self, points):
        self.score += points
        reached = [milestone for milestone in (25, 50, 75, 100) if self.score >= milestone and milestone not in self.completed_milestones]
        if reached:
            milestone = max(reached)
            self.completed_milestones.update(reached)
            self.start_celebration(milestone)

    def start_celebration(self, milestone):
        self.state = "celebration"
        self.celebration_milestone = milestone
        self.celebration_timer = 0.0
        self.celebration_kind = "victory" if milestone >= 100 else "milestone"
        self.create_particles((WIDTH // 2, 175), GOLD, 42)

    def continue_after_celebration(self):
        self.state = "playing"
        self.banner = "NEXT WAVE READY"
        self.banner_timer = 1.0

    def play_sound(self, sound):
        if self.audio_enabled and sound:
            sound.play()

    def spawn_interval(self):
        return max(0.16, (0.82 - self.level * 0.045) / self.mode["speed"])

    def create_particles(self, position, color, amount=10):
        self.particles.extend(Particle(position[0], position[1], color) for _ in range(amount))

    def update_rain(self, dt):
        intensity = self.world["rain"] if self.state == "playing" else 0.65
        for streak in self.rain:
            streak.update(dt, intensity)
        if self.state == "playing" and self.level >= 5:
            self.thunder_timer -= dt
            self.lightning_flash = max(0, self.lightning_flash - dt)
            if self.thunder_timer <= 0:
                self.thunder_timer = random.uniform(5.0, 10.0)
                self.lightning_flash = 0.20
                self.banner = "LIGHTNING STRIKE  •  HOLD STEADY"
                self.banner_timer = 1.0
                self.create_particles((random.randint(70, WIDTH - 70), 105), BLUE_LIGHT, 18)

    def spawn_water(self):
        kind = "normal"
        roll = random.random()
        if self.level >= 3 and roll < 0.08:
            kind = "gold"
        if self.level >= 5 and roll < 0.025:
            kind = "rainbow"
        return Water(kind=kind)

    def lose_life(self, position, banner):
        if self.shield:
            self.shield = 0
            self.banner = "SHIELD BLOCKED THE HAZARD"
            self.banner_timer = 1.15
            self.create_particles(position, PURPLE, 14)
            return False
        self.lives -= 1
        self.combo = 0
        self.banner = banner
        self.banner_timer = 1.0
        self.create_particles(position, RED, 9)
        self.play_sound(self.miss_sound)
        return self.lives <= 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.tank.move(direction, dt)
        self.total_time += dt
        self.spawn_timer += dt
        self.obstacle_timer += dt
        self.powerup_timer -= dt
        self.banner_timer = max(0, self.banner_timer - dt)
        self.world_banner_timer = max(0, self.world_banner_timer - dt)
        self.level = 1 + self.score // 10
        if self.world["name"] != self.last_world_name:
            self.last_world_name = self.world["name"]
            self.world_banner = self.world["event"]
            self.world_banner_timer = 2.0

        while self.spawn_timer >= self.spawn_interval():
            self.spawn_timer -= self.spawn_interval()
            self.waters.append(self.spawn_water())

        obstacle_interval = max(2.6, (7.0 - self.level * 0.35) / self.mode["speed"])
        if self.total_time > 5 and self.obstacle_timer >= obstacle_interval:
            self.obstacle_timer = 0
            self.obstacles.append(Obstacle())

        if self.powerup_timer <= 0 and len(self.powerups) < 2:
            self.powerups.append(PowerUp())
            self.powerup_timer = random.uniform(11, 16)

        water_speed = (205 + min(self.level * 14, 160)) * self.mode["speed"]
        for drop in self.waters[:]:
            drop.update(water_speed, dt)
            if drop.collides_with(self.tank):
                self.waters.remove(drop)
                self.drops_caught += 1
                self.combo += 1
                self.best_combo = max(self.best_combo, self.combo)
                multiplier = min(5, 1 + self.combo // 5)
                earned = drop.points * multiplier
                self.add_score(earned)
                drop_color = BLUE_LIGHT if drop.kind == "normal" else GOLD if drop.kind == "gold" else (255, 120, 220)
                self.create_particles(drop.rect.center, drop_color, 16 if drop.kind != "normal" else 12)
                self.play_sound(self.catch_sound)
                if self.drops_caught >= self.mission_target and not self.mission_claimed:
                    self.mission_claimed = True
                    self.add_score(10)
                    self.banner = "MISSION COMPLETE  +10"
                    self.banner_timer = 1.5
                    self.create_particles(drop.rect.center, GREEN, 20)
                elif drop.kind != "normal":
                    self.banner = f"{DROP_LABELS[drop.kind]}  x{multiplier}  = +{earned}"
                    self.banner_timer = 1.35
                elif self.combo % 5 == 0:
                    self.banner = f"COMBO x{multiplier}  +{multiplier}"
                    self.banner_timer = 1.25
            elif drop.missed():
                self.waters.remove(drop)
                if self.lose_life(drop.rect.center, "DROP MISSED"):
                    self.finish_round()
                    return

        for obstacle in self.obstacles[:]:
            obstacle.update(155 * self.mode["speed"] + self.level * 7, dt)
            if obstacle.collides_with(self.tank):
                self.obstacles.remove(obstacle)
                if self.lose_life(obstacle.rect.center, "TOXIC WASTE HIT"):
                    self.finish_round()
                    return
            elif obstacle.missed():
                self.obstacles.remove(obstacle)

        for powerup in self.powerups[:]:
            powerup.update(145 + self.level * 8, dt)
            if powerup.collides_with(self.tank):
                self.powerups.remove(powerup)
                if powerup.kind == "shield":
                    self.shield = 1
                    self.banner = "SHIELD READY"
                    color = PURPLE
                else:
                    self.add_score(5)
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
        world_tint = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        world_tint.fill((*self.world["tint"], 58))
        self.screen.blit(world_tint, (0, 0))
        cloud_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        cloud_alpha = min(100, 35 + self.level * 8)
        for x, y, size in ((45, 72, 1.0), (220, 94, 1.25), (405, 58, 0.9)):
            pygame.draw.ellipse(cloud_layer, (8, 18, 34, cloud_alpha), (x - 42 * size, y - 10 * size, 92 * size, 28 * size))
            pygame.draw.ellipse(cloud_layer, (8, 18, 34, cloud_alpha), (x - 20 * size, y - 24 * size, 58 * size, 38 * size))
        self.screen.blit(cloud_layer, (0, 0))
        rain_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for streak in self.rain:
            pygame.draw.line(rain_layer, (*BLUE_LIGHT, streak.alpha), (streak.x, int(streak.y)), (streak.x - 3, int(streak.y + streak.length)), 1)
        self.screen.blit(rain_layer, (0, 0))
        if self.lightning_flash > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((235, 245, 255, round(160 * self.lightning_flash / 0.20)))
            self.screen.blit(flash, (0, 0))

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

    def draw_special_drop(self, drop):
        color = GOLD if drop.kind == "gold" else (255, 120, 220)
        self.draw_drop_icon(drop.rect.center, color, 1.0)
        pygame.draw.circle(self.screen, WHITE, drop.rect.center, 13, 1)
        if drop.kind == "rainbow":
            for offset, ring_color in ((-4, RED), (0, ORANGE), (4, GREEN)):
                pygame.draw.arc(self.screen, ring_color, (drop.rect.x + 2, drop.rect.y + offset, drop.rect.width - 4, drop.rect.height - 4), 0.4, 2.7, 2)

    def draw_shield_icon(self, center, active=True):
        x, y = center
        color = PURPLE if active else MUTED
        points = [(x, y - 10), (x + 9, y - 5), (x + 7, y + 7), (x, y + 12), (x - 7, y + 7), (x - 9, y - 5)]
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.line(self.screen, NAVY, (x, y - 5), (x, y + 6), 2)
        pygame.draw.line(self.screen, NAVY, (x - 4, y), (x + 4, y), 2)

    def draw_trash_icon(self, center):
        x, y = center
        pygame.draw.rect(self.screen, TOXIC, (x - 8, y - 7, 16, 17), border_radius=3)
        pygame.draw.rect(self.screen, TOXIC, (x - 10, y - 10, 20, 3), border_radius=2)
        pygame.draw.line(self.screen, NAVY, (x - 3, y - 3), (x - 3, y + 6), 2)
        pygame.draw.line(self.screen, NAVY, (x + 3, y - 3), (x + 3, y + 6), 2)

    def draw_hud(self):
        pygame.draw.rect(self.screen, (5, 17, 31), (0, 0, WIDTH, 82))
        pygame.draw.line(self.screen, BLUE, (0, 81), (WIDTH, 81), 2)
        self.screen.blit(self.font_tiny.render("SAVE WATER", True, BLUE_LIGHT), (17, 10))
        self.screen.blit(self.font_tiny.render(f"{self.mode['name']}  •  LV {self.level}", True, ORANGE), (17, 31))
        self.draw_text(self.world["name"], self.font_tiny, self.world["accent"], (82, 57))
        self.draw_text(str(self.score), self.font_large, WHITE, (244, 24))
        self.draw_text("SCORE", self.font_tiny, MUTED, (244, 51))
        for index in range(self.mode["lives"]):
            self.draw_heart((355 + index * 17, 18), RED if index < self.lives else NAVY_LIGHT, 0.68)
        self.draw_text("LIVES", self.font_tiny, MUTED, (382, 48))
        if self.shield:
            self.draw_shield_icon((470, 22))
        pygame.draw.rect(self.screen, NAVY_LIGHT, (175, 72, 155, 4), border_radius=2)
        mission_progress = min(1, self.drops_caught / self.mission_target)
        pygame.draw.rect(self.screen, GREEN, (175, 72, round(155 * mission_progress), 4), border_radius=2)
        self.draw_text(f"MISSION {self.drops_caught}/{self.mission_target}", self.font_tiny, MUTED, (252, 76))

    def draw_powerup(self, powerup):
        x, y = powerup.rect.centerx, powerup.rect.centery + powerup.bob_offset
        color = PURPLE if powerup.kind == "shield" else ORANGE
        pygame.draw.circle(self.screen, (8, 25, 43), (x, y), 18)
        pygame.draw.circle(self.screen, color, (x, y), 15, 2)
        if powerup.kind == "shield":
            self.draw_shield_icon((x, y), True)
        else:
            pygame.draw.polygon(self.screen, color, [(x + 2, y - 11), (x - 6, y + 1), (x - 1, y + 1), (x - 3, y + 11), (x + 7, y - 3), (x + 1, y - 3)])

    def draw_obstacle(self, obstacle):
        self.draw_trash_icon((obstacle.rect.centerx + obstacle.wobble, obstacle.rect.centery))
        pygame.draw.circle(self.screen, TOXIC, obstacle.rect.center, 18, 1)

    def draw_particles(self):
        for particle in self.particles:
            alpha = round(255 * min(1, particle.life / particle.max_life))
            layer = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(layer, (*particle.color, alpha), (5, 5), particle.radius)
            self.screen.blit(layer, (round(particle.x - 5), round(particle.y - 5)))

    def draw_playfield(self):
        self.draw_background()
        for drop in self.waters:
            if drop.kind == "normal":
                self.screen.blit(self.water_image, drop.rect)
            else:
                self.draw_special_drop(drop)
        for obstacle in self.obstacles:
            self.draw_obstacle(obstacle)
        for powerup in self.powerups:
            self.draw_powerup(powerup)
        self.draw_particles()
        shadow = pygame.Surface((TANK_WIDTH + 20, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 95), shadow.get_rect())
        self.screen.blit(shadow, (self.tank.rect.centerx - shadow.get_width() // 2, HEIGHT - 27))
        self.screen.blit(self.tank_image, self.tank.rect)
        self.draw_hud()
        if self.combo >= 2:
            self.draw_text(f"COMBO {self.combo}", self.font_small, GREEN, (WIDTH // 2, 101))
        if self.banner_timer > 0:
            self.draw_text(self.banner, self.font_body, ORANGE, (WIDTH // 2, 126))
        if self.world_banner_timer > 0:
            self.draw_text(self.world_banner, self.font_small, self.world["accent"], (WIDTH // 2, 148))

    def draw_panel(self, height=250):
        panel = pygame.Surface((WIDTH - 56, height), pygame.SRCALPHA)
        panel.fill((5, 18, 32, 232))
        top = (HEIGHT - height) // 2
        self.screen.blit(panel, (28, top))
        pygame.draw.rect(self.screen, BLUE, (28, top, WIDTH - 56, height), 2, border_radius=12)

    def draw_trophy(self, center, scale=1.0):
        x, y = center
        color = GOLD
        bowl = pygame.Rect(x - round(16 * scale), y - round(12 * scale), round(32 * scale), round(25 * scale))
        pygame.draw.rect(self.screen, color, bowl, border_radius=6)
        pygame.draw.arc(self.screen, color, (x - round(28 * scale), y - round(10 * scale), round(18 * scale), round(24 * scale)), math.pi / 2, math.pi * 1.5, max(2, round(3 * scale)))
        pygame.draw.arc(self.screen, color, (x + round(10 * scale), y - round(10 * scale), round(18 * scale), round(24 * scale)), -math.pi / 2, math.pi / 2, max(2, round(3 * scale)))
        pygame.draw.rect(self.screen, color, (x - round(4 * scale), y + round(12 * scale), round(8 * scale), round(12 * scale)))
        pygame.draw.rect(self.screen, color, (x - round(18 * scale), y + round(22 * scale), round(36 * scale), round(6 * scale)), border_radius=3)

    def draw_celebration(self):
        self.draw_playfield()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((3, 12, 24, 190))
        self.screen.blit(overlay, (0, 0))
        self.draw_panel(285)
        pulse = 1 + 0.08 * math.sin(self.celebration_timer * 5)
        self.draw_trophy((WIDTH // 2, 126), pulse)
        if self.celebration_kind == "victory":
            self.draw_text("LEGENDARY VICTORY", self.font_large, GOLD, (WIDTH // 2, 175))
            self.draw_text("You are a true Water Guardian.", self.font_body, WHITE, (WIDTH // 2, 208))
        else:
            self.draw_text("MILESTONE UNLOCKED", self.font_large, GOLD, (WIDTH // 2, 175))
            self.draw_text(f"{self.celebration_milestone} drops saved!", self.font_body, WHITE, (WIDTH // 2, 208))
        self.draw_text("Your storm skills are making a difference.", self.font_small, MUTED, (WIDTH // 2, 238))
        pygame.draw.rect(self.screen, BLUE, (105, 264, 290, 48), border_radius=10)
        self.draw_text("ENTER  Continue the mission", self.font_body, NAVY, (WIDTH // 2, 288))
        self.draw_text("ESC  Return to menu", self.font_small, MUTED, (WIDTH // 2, 338))

    def draw_menu(self):
        self.draw_background()
        self.draw_panel(350)
        self.draw_drop_icon((WIDTH // 2, 70), BLUE_LIGHT, 1.4)
        self.draw_text("SAVE", self.font_title, WHITE, (WIDTH // 2, 112))
        self.draw_text("WATER", self.font_title, BLUE_LIGHT, (WIDTH // 2, 152))
        self.draw_text("STORM CATCHER", self.font_tiny, ORANGE, (WIDTH // 2, 187))
        pygame.draw.rect(self.screen, BLUE, (128, 215, 244, 52), border_radius=10)
        self.draw_text("PRESS ENTER TO PLAY", self.font_body, NAVY, (WIDTH // 2, 241))
        self.draw_text(f"MODE  {self.mode['name']}", self.font_small, GREEN, (WIDTH // 2, 294))
        self.draw_text("S  Settings", self.font_small, WHITE, (WIDTH // 2, 320))
        self.draw_text("←  →   Move tank", self.font_small, WHITE, (WIDTH // 2, 346))
        self.draw_text("P Pause   M Sound   ESC Quit", self.font_tiny, MUTED, (WIDTH // 2, 370))
        self.draw_text(f"BEST SCORE  {self.high_score}", self.font_small, GREEN, (WIDTH // 2, 398))

    def draw_settings(self):
        self.draw_background()
        self.draw_panel(310)
        self.draw_text("SETTINGS", self.font_title, WHITE, (WIDTH // 2, 125))
        self.draw_text("Choose your storm", self.font_body, MUTED, (WIDTH // 2, 160))
        pygame.draw.rect(self.screen, NAVY_LIGHT, (75, 190, 350, 66), border_radius=10)
        self.draw_text("‹", self.font_title, BLUE_LIGHT, (105, 223))
        self.draw_text(self.mode["name"], self.font_large, BLUE_LIGHT, (WIDTH // 2, 216))
        self.draw_text("›", self.font_title, BLUE_LIGHT, (395, 223))
        self.draw_text(self.mode["description"], self.font_small, MUTED, (WIDTH // 2, 242))
        self.draw_text(f"Lives: {self.mode['lives']}     Drop speed: {self.mode['speed']:.2f}x", self.font_small, WHITE, (WIDTH // 2, 288))
        self.draw_text("← → Change mode   ENTER Start   ESC Back", self.font_small, WHITE, (WIDTH // 2, 334))

    def draw_pause(self):
        self.draw_playfield()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 14, 25, 175))
        self.screen.blit(overlay, (0, 0))
        self.draw_panel(190)
        self.draw_text("STORM ON HOLD", self.font_title, WHITE, (WIDTH // 2, 190))
        self.draw_text("The next drop is waiting for you.", self.font_body, BLUE_LIGHT, (WIDTH // 2, 225))
        self.draw_text("P / ENTER  Resume play", self.font_small, WHITE, (WIDTH // 2, 260))
        self.draw_text("ESC  Save this run and return to menu", self.font_small, MUTED, (WIDTH // 2, 286))

    def draw_game_over(self):
        self.draw_background()
        self.draw_panel(330)
        self.draw_text("STORM COMPLETE", self.font_large, WHITE, (WIDTH // 2, 112))
        self.draw_drop_icon((WIDTH // 2, 155), BLUE_LIGHT, 1.0)
        self.draw_text(str(self.score), self.font_title, BLUE_LIGHT, (WIDTH // 2, 196))
        self.draw_text(f"SCORE  •  {self.mode['name']}  •  LEVEL {self.level}", self.font_tiny, MUTED, (WIDTH // 2, 225))
        self.draw_text(f"Best combo  {self.best_combo}     Best score  {self.high_score}", self.font_small, GREEN, (WIDTH // 2, 253))
        mission_text = "MISSION COMPLETE" if self.mission_claimed else f"Mission: catch {self.mission_target} drops"
        self.draw_text(mission_text, self.font_small, ORANGE if self.mission_claimed else MUTED, (WIDTH // 2, 282))
        self.draw_text("WATER-SAVING TIP", self.font_tiny, BLUE_LIGHT, (WIDTH // 2, 315))
        self.draw_text(self.end_tip, self.font_tiny, WHITE, (WIDTH // 2, 337))
        self.draw_text("R  Play again     ESC  Menu", self.font_small, WHITE, (WIDTH // 2, 374))

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "settings":
            self.draw_settings()
        elif self.state == "playing":
            self.draw_playfield()
        elif self.state == "paused":
            self.draw_pause()
        elif self.state == "celebration":
            self.draw_celebration()
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
        elif self.state == "menu" and event.key == pygame.K_s:
            self.state = "settings"
        elif self.state == "settings" and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.mode_index = (self.mode_index + (1 if event.key == pygame.K_RIGHT else -1)) % len(MODES)
        elif self.state == "settings" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.start_round()
        elif self.state == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.start_round()
        elif self.state == "playing" and event.key == pygame.K_p:
            self.state = "paused"
        elif self.state == "paused" and event.key in (pygame.K_p, pygame.K_RETURN, pygame.K_SPACE):
            self.state = "playing"
        elif self.state == "celebration" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.continue_after_celebration()
        elif self.state == "celebration" and event.key == pygame.K_p:
            self.continue_after_celebration()
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
            elif running and self.state == "celebration":
                self.celebration_timer += dt
                for particle in self.particles[:]:
                    particle.update(dt)
                    if not particle.alive:
                        self.particles.remove(particle)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
