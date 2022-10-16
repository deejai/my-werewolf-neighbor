import math
import pygame

import config
from gameobjects.base import GameObject
from gameobjects.player import Player

class Bullet(GameObject):
    def __init__(self, direction):
        super().__init__(16, 16)
        self.direction = direction
        self.sprite = pygame.image.load(config.ROOT_DIR + "assets/sprites/silver_bullet.png")
        self.speed = 10
        self.damage = 10

    def update(self, world):
        super().update(world)
        if(self.direction == "right"):
            self.x += self.speed
        else:
            self.x -= self.speed

        if(self.x > config.GAME_WIDTH or self.x < 0):
            world.active_objects.remove(self)

        for obj in world.active_objects:
            if(isinstance(obj, Player)):
                if(math.sqrt(math.pow(obj.x - self.x, 2) + math.pow(obj.y - self.y, 2)) < 8):
                    if(self.y + self.height > obj.y and self.y < obj.y + obj.height):
                        obj.hp -= self.damage
                        world.active_objects.remove(self)
                        world.play_werewolf_hurt_sound()
                        break

    def draw(self, screen):
        super().draw(screen)
        sprite = self.sprite
        if(self.direction == "left"):
            sprite = pygame.transform.flip(sprite, True, False)
        screen.blit(sprite, (self.x, self.y))
