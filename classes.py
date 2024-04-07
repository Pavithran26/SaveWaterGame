import pygame
import random

WIDTH = 500
HEIGHT = 500

WATER_HEIGHT = 37
WATER_WIDTH = 30

TANK_HEIGHT = 80
TANK_WIDTH = 80

TANK_VEL = 7


class water:
    def __init__(self):
        self.rec = pygame.Rect(
            random.uniform(0, WIDTH - WATER_WIDTH),
            0 - WATER_HEIGHT,
            WATER_WIDTH,
            WATER_HEIGHT,
        )

    def check_water(self):
        if self.rec.y > HEIGHT - WATER_HEIGHT:
            return False
        else:
            return True
    
    def check_coll(self,tank):
        if self.rec.colliderect(tank.rec):
            return True
        else:
            return False


class bask:
    def __init__(self):
        self.rec = pygame.Rect(
            (WIDTH - TANK_HEIGHT) / 2,
            HEIGHT - TANK_HEIGHT,
            TANK_WIDTH,
            TANK_HEIGHT,
        )

    def movement(self, dir):
            if dir == "r" and self.rec.x < (WIDTH - TANK_WIDTH):
                self.rec.x += TANK_VEL
            if dir == "l" and self.rec.x > 0 :
                self.rec.x -= TANK_VEL
