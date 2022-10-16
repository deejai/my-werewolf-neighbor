import pygame
import math

import config
from gameobjects.base import GameObject
from utilities import fall

class Detective(GameObject):
    def __init__(self):
        super().__init__(64, 64)
        self.idle_sprite_sheet = pygame.image.load(config.ROOT_DIR + "assets/sprites/detective_idle.png")
        self.idle_sprites = []
        for i in range(4):
            self.idle_sprites.append(self.idle_sprite_sheet.subsurface((i*32, 0, 32, 32)))

        investigate_sprite_sheet = pygame.image.load(config.ROOT_DIR + "assets/sprites/detective_investigate.png")
        self.investigate_sprites = []
        for i in range(4):
            self.investigate_sprites.append(investigate_sprite_sheet.subsurface((i*32, 0, 32, 32)))

        self.following = False
        self.follow_cooldown = 0
        self.follow_tick = 0
        self.follow_duration = 30

        self.investigating = False
        self.investigate_cooldown = 0
        self.investigate_tick = 0
        self.investigate_duration = 50

        self.sprites = self.idle_sprites

        self.frame_duration = 3
        self.animation_tick = 0

        self.y_velocity = 0

        self.dead = False

        self.direction = "right"

        self.voice_cooldown = 0

    def update(self, world):
        super().update(world)

        fall(self, world)

        if(self.investigating):
            if(self.investigate_tick >= self.investigate_duration):
                world.game_over("investigated")
            else:
                self.investigate_tick += 1
        else:
            self.investigate_tick = 0

        if(self.following):
            if(self.follow_tick >= self.follow_duration):
                self.following = False
                self.follow_tick = 0
                self.follow_duration = 0
            else:
                self.follow_tick += 1
                if(math.sqrt(math.pow(world.player.x - self.x, 2) + math.pow(world.player.y - self.y, 2)) > 25):
                    if(self.direction == "left"):
                        self.x -= 1
                    else:
                        self.x += 1


        # if the player is close, but not too close, play a "notice" sound and start following the player
        if(math.sqrt(math.pow(world.player.x - self.x, 2) + math.pow(world.player.y - self.y, 2)) < 200):
            if self.voice_cooldown <= 0:
                world.play_detective_notice_sound()
                self.voice_cooldown = 100

            if(self.following == False and self.follow_cooldown <= 0):
                self.following = True
                self.follow_tick = 0

                if(world.player.x > self.x):
                    self.direction = "right"
                else:
                    self.direction = "left"

                self.follow_cooldown = 100

        if(self.follow_cooldown > 0):
            self.follow_cooldown -= 1

        if(self.investigate_cooldown > 0):
            self.investigate_cooldown -= 1

        # if the player is very close, start investigating and play an "investigate" sound
        if(math.sqrt(math.pow(world.player.x - self.x, 2) + math.pow(world.player.y - self.y, 2)) < 100):
            if self.voice_cooldown <= 0:
                world.play_detective_investigate_sound()
                self.voice_cooldown = 100

            self.investigating = True

        else:
            self.investigating = False
            self.investigate_tick = 0

    def draw(self, screen):
        if(self.investigating):
            current_sprite_index = int(len(self.investigate_sprites) * self.investigate_tick / self.frame_duration / self.investigate_duration) % len(self.investigate_sprites)
            current_sprite = self.investigate_sprites[current_sprite_index]
            image = pygame.transform.scale(current_sprite, (self.width, self.height))
            if(self.direction == "left"):
                image = pygame.transform.flip(image, True, False)
            screen.blit(image, (self.x-self.width/2, self.y-self.height/2))
            current_sprite = self.investigate_sprites[current_sprite_index]
        else:
            current_sprite_index = int(self.animation_tick / self.frame_duration)
            current_sprite = self.idle_sprites[current_sprite_index]

        image = pygame.transform.scale(current_sprite, (self.width, self.height))
        if(self.direction == "left"):
            image = pygame.transform.flip(image, True, False)
        screen.blit(image, (self.x-self.width/2, self.y-self.height/2))

        self.animation_tick = (self.animation_tick + 1) % (len(self.idle_sprites) * self.frame_duration)

    def reset(self):
        super().reset()
        self.following = False
        self.follow_cooldown = 0
        self.follow_tick = 0

        self.investigating = False
        self.investigate_cooldown = 0
        self.investigate_tick = 0

        self.voice_cooldown = 0

        self.sprites = self.idle_sprites

        self.animation_tick = 0
