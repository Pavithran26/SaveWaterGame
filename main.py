import pygame
from classes import *

pygame.init()
pygame.mixer.init()
pygame.font.init()
FPS = 60
WIDTH = 500
HEIGHT = 500
WATER = pygame.transform.scale(pygame.image.load("water.png"), (WATER_WIDTH, WATER_HEIGHT))
TANK = pygame.transform.scale(
    pygame.image.load("tank.png"), (TANK_WIDTH, TANK_HEIGHT)
)
BACKGROUND = pygame.transform.scale(
    pygame.image.load("background.jpg"), (WIDTH, HEIGHT)
)

WATER_VEL = 5
TANK_VEL = 7

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SAVE WATER")

p_sound = pygame.mixer.Sound("point_sound.mp3")
h_sound = pygame.mixer.Sound("water_sound.mp3")

FONT1 = pygame.font.SysFont("fixedsys", 20)


def check_waters(waters, health):
    for water in waters:
        if water.check_water():
            water.rec.y += WATER_VEL
        else:
            waters.remove(water)
            health -= 1
            h_sound.play()
    return waters, health


def draw(waters, tank, health, points):
    WIN.fill((0, 0, 0))
    WIN.blit(BACKGROUND, (0, 0))
    for water in waters:
        WIN.blit(WATER, (water.rec.x, water.rec.y))
    WIN.blit(TANK, (tank.rec.x, tank.rec.y))
    text1 = FONT1.render("Health:" + str(health), 1, (255, 0, 0))
    text2 = FONT1.render("Score:" + str(points), 1, (0, 255, 0))
    WIN.blit(text2, (0, 0))
    WIN.blit(text1, (WIDTH - text1.get_width(), 0))


def tank_move(KP, tank):
    if KP[pygame.K_RIGHT]:
        tank.movement("r")
    if KP[pygame.K_LEFT]:
        tank.movement("l")


def check_coll(tank, waters, points):
    for water in waters:
        if water.check_coll(tank):
            waters.remove(water)
            points += 1
            p_sound.play()
        else:
            pass
    return waters, points


def main():
    global TANK_VEL

    pygame.mixer.music.load("background.mp3")
    pygame.mixer.music.play(-1, 0, 0)

    run = True
    clock = pygame.time.Clock()
    waters = []
    tank = bask()
    time = pygame.time.get_ticks()
    n = 1
    health = 10
    points = 0

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False

                break

        if health == 0:

            pygame.quit()
            import sys

            sys.exit()

        x = pygame.time.get_ticks() - time
        if x > 1000 / n:
            water1 = water()
            waters.append(water1)
            time = pygame.time.get_ticks()
            n += n / 100
            TANK_VEL += 0.001 * n / 1000

        KP = pygame.key.get_pressed()

        tank_move(KP, tank)
        waters, health = check_waters(waters, health)
        waters, points = check_coll(tank, waters, points)
        draw(waters, tank, health, points)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
