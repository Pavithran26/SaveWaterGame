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
