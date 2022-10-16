import pygame
import random

import config
from gameobjects.base import GameObject

class Scenery(GameObject):
    def __init__(self, image_path, width=None, height=None):
        super().__init__(width, height)
        image = pygame.image.load(config.ROOT_DIR + image_path)
        if(width==None or height==None):
            self.width = image.get_width()
            self.height = image.get_height()
        self.image = pygame.transform.scale(image, (self.width, self.height))

    def draw(self, screen):
        screen.blit(self.image, (self.x-self.width/2, self.y-self.height/2))

class Building(Scenery):
    def __init__(self, image_path, width=None, height=None):
        super().__init__(image_path, width, height)

    def update(self, world):
        # spawn citizens at random intervals
        if random.randint(0, 60) == 0:
            inactive_citizen = [x for x in world.citizens if x.active == False and x.dead == False]
            if len(inactive_citizen) == 0:
                return
            citizen = random.choice(inactive_citizen)
            if(citizen):
                citizen.active = True
                citizen.reset()
                key_num = 0
                key = f"rando_citizen_{key_num}"

                while(world.objects.get(key)):
                    key_num += 1
                    key = f"rando_citizen_{key_num}"

                world.objects[f"rando_citizen_{key_num}"] = citizen
                world.populate(key, self.x, self.y + self.height/2 - citizen.height/2, first=True)
