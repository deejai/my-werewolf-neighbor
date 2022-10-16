from random import random
import pygame
import math

import config
from gameobjects.base import GameObject
from gameobjects.bullet import Bullet
from utilities import fall

class Hunter(GameObject):
    def __init__(self):
        super().__init__(32, 64)
        self.idle_sprite_sheet = pygame.image.load(config.ROOT_DIR + "assets/sprites/hunter.png")
        self.idle_sprites = []
        for i in range(2):
            self.idle_sprites.append(self.idle_sprite_sheet.subsurface((i*32, 0, 32, 64)))

        self.sprites = self.idle_sprites

        self.frame_duration = 3
        self.animation_tick = 0

        self.y_velocity = 0

        self.dead = False

        self.direction = "right"

        self.voice_cooldown = 0

        self.shoot_cooldown = 0

    def update(self, world):
        super().update(world)

        fall(self, world)

        if(math.sqrt(math.pow(world.player.x - self.x, 2) + math.pow(world.player.y - self.y, 2)) > 80):
            if(self.x > world.player.x):
                self.x -= 1
                self.direction = "left"
            else:
                self.x += 1
                self.direction = "right"

        if(self.voice_cooldown > 0):
            self.voice_cooldown -= 1

        if(self.shoot_cooldown > 0):
            self.shoot_cooldown -= 1

        if(self.voice_cooldown <= 0):
            if(random() < 0.1):
                self.voice_cooldown = 75
                world.play_hunter_taunt_sound()

        if(self.voice_cooldown < 50 and self.voice_cooldown > 25 and self.shoot_cooldown <= 0):
            self.shoot_cooldown = 50
            world.play_gunshot_sound()

            bullet = Bullet(self.direction)
            bullet.x = self.x + (-1 if self.direction == "left" else 1) * 8
            bullet.y = self.y
            bullet.direction = self.direction
            bullet.active = True
            world.active_objects.insert(1, bullet)

    def draw(self, screen):
        current_sprite_index = int(self.animation_tick / self.frame_duration)
        current_sprite = self.idle_sprites[current_sprite_index]

        image = pygame.transform.scale(current_sprite, (self.width, self.height))
        if(self.direction == "right"):
            image = pygame.transform.flip(image, True, False)
        screen.blit(image, (self.x-self.width/2, self.y-self.height/2))

        self.animation_tick = (self.animation_tick + 1) % (len(self.idle_sprites) * self.frame_duration)

    def reset(self):
        super().reset()

        self.voice_cooldown = 0

        self.sprites = self.idle_sprites

        self.animation_tick = 0
