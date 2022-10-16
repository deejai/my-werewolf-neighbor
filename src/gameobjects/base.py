import math
import pygame
import random

import config

death_sprite_sheet = pygame.image.load(config.ROOT_DIR + "assets/sprites/bone_splat.png")
death_sprites = []
for i in range(0, 4):
    death_sprites.append(death_sprite_sheet.subsurface(i*32, 0, 32, 32))

class GameObject:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.active = False

    def update(self, world):
        pass

    def draw(self, screen):
        pass

    def reset(self):
        self.active = False

class Platform(GameObject):
    def __init__(self, image_path, width, height):
        super().__init__(width, height)
        image = pygame.image.load(config.ROOT_DIR + image_path)
        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.platform = True

    def draw(self, screen):
        screen.blit(self.image, (self.x-self.width/2, self.y-self.height/2))
            
        if config.DEBUG:
            pygame.draw.rect(screen, (255, 0, 0), (self.x-self.width/2, self.y-self.height/2, self.width, self.height), 2)
