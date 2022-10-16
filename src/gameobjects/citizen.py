import pygame
import random
import math

import config
from utilities import fall
from gameobjects.base import GameObject, death_sprites

class Citizen(GameObject):
    def __init__(self, image_path, width, height):
        super().__init__(width, height)
        idle_sprite_sheet = pygame.image.load(image_path)
        self.idle_sprites = []
        for i in range(2):
            self.idle_sprites.append(idle_sprite_sheet.subsurface((i*32, 0, 32, 32)))

        self.frame_duration = 3
        self.animation_tick = 0

        self.run_boost = 0
        self.run_boost_cool_down = 0

        self.y_velocity = 0
        self.grounded = False

        self.direction = "right"
        self.direction_cool_down = 0

        self.voice_cooldown = 0

        self.gossip_cooldown = random.randint(50, 100)

        self.dead = False
        self.death_tick = 0

    def update(self, world):
        if(self.dead):
            if(self.death_tick >= 4):
                world.depopulate(self)
                self.death_tick = 0
            return

        # walk randomly
        if self.direction_cool_down <= 0:
            self.direction = random.choice(["left", "right"])
            self.direction_cool_down = random.randint(10, 30)
        else:
            self.direction_cool_down -= 1

        if self.direction == "left" and self.x > 0:
            if(self.run_boost > 0):
                self.x -= 2
            else:
                self.x -= 1
        elif self.direction == "right" and self.x < config.GAME_WIDTH:
            if(self.run_boost > 0):
                self.x += 2
            else:
                self.x += 1

        fall(self, world)

        # reduce cooldowns

        if(self.voice_cooldown > 0):
            self.voice_cooldown -= 1

        if(self.run_boost_cool_down > 0):
            self.run_boost_cool_down -= 1

        if(self.run_boost > 0):
            self.run_boost -= 1

        if(self.gossip_cooldown > 0):
            self.gossip_cooldown -= 1

        # during night time, if the player is close to the citizen, make them run and say something
        if(world.phase == "night" and math.sqrt(math.pow(world.player.x - self.x, 2) + math.pow(world.player.y - self.y, 2)) < 100):
                if self.voice_cooldown <= 0:
                    world.play_citizen_scared_sound()
                    self.voice_cooldown = 100

                if(self.run_boost <= 0 and self.run_boost_cool_down <= 0):
                    self.run_boost = 20
                    self.run_boost_cool_down = 100

                if(world.player.x > self.x):
                    self.direction = "left"
                else:
                    self.direction = "right"

                self.direction_cool_down = 10

        if(world.phase == "day" and self.gossip_cooldown <= 0):
            self.gossip_cooldown = random.randint(50, 100)
            world.play_citizen_gossip_sound()

    def get_bitten(self, world):
        self.dead = True

    def draw(self, screen):
        if(self.dead):
            if(self.death_tick < 4):
                screen.blit(death_sprites[self.death_tick], (self.x-self.width/2, self.y-self.height/2))
            self.death_tick += 1
            return

        current_sprite_index = int(self.animation_tick / self.frame_duration)
        current_sprite = self.idle_sprites[current_sprite_index]
        image = pygame.transform.scale(current_sprite, (self.width, self.height))
        screen.blit(image, (self.x-self.width/2, self.y-self.height/2))

        self.animation_tick = (self.animation_tick + 1) % (len(self.idle_sprites) * self.frame_duration)
