from typing import Sequence
import pygame
import sys

import config
from world import World

pygame.init()

screen = pygame.display.set_mode((config.GAME_WIDTH, config.GAME_HEIGHT))
pygame.display.set_caption("My Game")

clock = pygame.time.Clock()
framerate = 120 # 0 = unlimited
update_wait = 1000 / 30
halt = False
last_update = 0

world = World()

def process_inputs(prev_keys = None):
    if prev_keys is None:
        prev_keys = {}

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        world.player.actions.add("left")
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        world.player.actions.add("right")
    if keys[pygame.K_SPACE] and world.player.grounded == True and not prev_keys[pygame.K_SPACE]:
        world.player.actions.add("jump")
    if keys[pygame.K_LCTRL] and not prev_keys[pygame.K_LCTRL]:
        if world.phase == "night" and world.player.attack_cool_down == 0:
            world.player.actions.add("attack")
        if world.phase == "day" and world.player.interrupt_cool_down == 0:
            world.player.actions.add("interrupt")

    return keys

def update():
    for obj in world.active_objects:
        obj.update(world)

    world.player.actions.clear()

def draw():
    screen.fill((40, 0, 40))

    for obj in reversed(world.active_objects):
        obj.draw(screen)

    world.draw_bars(screen)

    pygame.display.flip()

def run():
    global halt
    global last_update

    pygame.display.set_caption("My Werewolf Neighbour")
    world.start_night()
    last_update = pygame.time.get_ticks()
    prev_keys = {}
    while not halt:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if world.phase_timer >= config.PHASE_DURATION:
            if world.phase == "day":
                world.start_night()
            elif world.phase == "night":
                world.start_day()

        # update inputs
        prev_keys = process_inputs(prev_keys)

        # if enough time has passed, update game state
        if pygame.time.get_ticks() - last_update > update_wait:
            update()
            last_update = pygame.time.get_ticks()
            draw()

        clock.tick(framerate)
        world.phase_timer += clock.get_time()
        # fps = clock.get_fps()
        # pygame.display.set_caption("FPS: " + str(fps))

def main():
    run()

if __name__ == "__main__":
    main()
