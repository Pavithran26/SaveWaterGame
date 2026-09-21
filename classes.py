import math
import random

import pygame


WIDTH = 500
HEIGHT = 500
WATER_WIDTH = 30
WATER_HEIGHT = 37
TANK_WIDTH = 80
TANK_HEIGHT = 80


class Water:
    """A falling water drop represented by a collision rectangle."""

    def __init__(self, x=None):
        if x is None:
            x = random.randint(0, WIDTH - WATER_WIDTH)
        self.rect = pygame.Rect(x, -WATER_HEIGHT, WATER_WIDTH, WATER_HEIGHT)

    def update(self, speed, dt):
        self.rect.y += round(speed * dt)

    def missed(self):
        return self.rect.top > HEIGHT

    def collides_with(self, tank):
        return self.rect.colliderect(tank.rect)


class Tank:
    """Player-controlled catcher constrained to the window."""

    def __init__(self, speed=320):
        self.rect = pygame.Rect(
            (WIDTH - TANK_WIDTH) // 2,
            HEIGHT - TANK_HEIGHT - 12,
            TANK_WIDTH,
            TANK_HEIGHT,
        )
        self.speed = speed

    def move(self, direction, dt):
        self.rect.x += round(direction * self.speed * dt)
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

    def reset(self):
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 12


class RainDrop:
    """A lightweight decorative rain streak drawn behind the playfield."""

    def __init__(self):
        self.x = random.randrange(WIDTH)
        self.y = random.randrange(-HEIGHT, HEIGHT)
        self.length = random.randrange(7, 19)
        self.speed = random.randrange(220, 430)
        self.alpha = random.randrange(35, 115)

    def update(self, dt, intensity=1.0):
        self.y += self.speed * intensity * dt
        if self.y > HEIGHT + self.length:
            self.x = random.randrange(WIDTH)
            self.y = random.randrange(-80, -10)


class Particle:
    """Short-lived sparkle used for catch and power-up feedback."""

    def __init__(self, x, y, color):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(35, 135)
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(0.35, 0.75)
        self.max_life = self.life
        self.color = color
        self.radius = random.randint(2, 4)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 90 * dt
        self.life -= dt

    @property
    def alive(self):
        return self.life > 0


class PowerUp:
    """A collectible with either a protective shield or score bonus."""

    TYPES = ("shield", "bonus")

    def __init__(self, kind=None):
        self.kind = kind or random.choice(self.TYPES)
        self.rect = pygame.Rect(random.randint(18, WIDTH - 42), -28, 28, 28)
        self.phase = random.random() * math.tau

    def update(self, speed, dt):
        self.rect.y += round(speed * dt)
        self.phase += dt * 4

    def missed(self):
        return self.rect.top > HEIGHT

    def collides_with(self, tank):
        return self.rect.colliderect(tank.rect)

    @property
    def bob_offset(self):
        return round(math.sin(self.phase) * 3)


class Obstacle:
    """Toxic plastic waste that penalizes careless movement."""

    def __init__(self):
        self.rect = pygame.Rect(random.randint(20, WIDTH - 48), -28, 28, 28)
        self.phase = random.random() * math.tau

    def update(self, speed, dt):
        self.rect.y += round(speed * dt)
        self.phase += dt * 3

    def missed(self):
        return self.rect.top > HEIGHT

    def collides_with(self, tank):
        return self.rect.colliderect(tank.rect)

    @property
    def wobble(self):
        return round(math.sin(self.phase) * 2)
