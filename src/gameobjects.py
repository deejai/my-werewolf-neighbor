import math
import pygame
import random

import config
from utilities import clamp, fall

death_sprite_sheet = pygame.image.load("assets/sprites/bone_splat.png")
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
        image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.platform = True

    def draw(self, screen):
        screen.blit(self.image, (self.x-self.width/2, self.y-self.height/2))
            
        if config.DEBUG:
            pygame.draw.rect(screen, (255, 0, 0), (self.x-self.width/2, self.y-self.height/2, self.width, self.height), 2)

class Scenery(GameObject):
    def __init__(self, image_path, width=None, height=None):
        super().__init__(width, height)
        image = pygame.image.load(image_path)
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
        if random.randint(0, 20) == 0:
            inactive_citizen = [x for x in world.citizens if x.active == False and x.dead == False]
            if len(inactive_citizen) == 0:
                return
            citizen = random.choice(inactive_citizen)
            if(citizen):
                citizen.active = True
                key_num = 0
                key = f"rando_citizen_{key_num}"

                while(world.objects.get(key)):
                    key_num += 1
                    key = f"rando_citizen_{key_num}"

                world.objects[f"rando_citizen_{key_num}"] = citizen
                world.populate(key, self.x, self.y + self.height/2 - citizen.height/2, first=True)

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

class Player(GameObject):
    def __init__(self):
        super().__init__(64, 64)
        self.sprite_index = 0
        self.speed = 5
        self.direction = "right"

        idle_sprite_sheet = pygame.image.load("assets/sprites/werewolf_spritesheet.png")
        self.idle_sprites = []
        for i in range(0, 1):
            self.idle_sprites.append(idle_sprite_sheet.subsurface((i*32, 0, 32, 32)))

        walking_sprite_sheet = pygame.image.load("assets/sprites/werewolf_spritesheet.png")
        self.walking_sprites = []
        for i in range(0, 6):
            self.walking_sprites.append(walking_sprite_sheet.subsurface((i*32, 0, 32, 32)))

        attack_sprite_sheet = pygame.image.load("assets/sprites/werewolf_attack_spritesheet.png")
        self.attack_sprites = []
        for i in range(0, 5):
            self.attack_sprites.append(attack_sprite_sheet.subsurface((i*32, 0, 32, 32)))

        self.sprites = self.idle_sprites
        self.animation_tick = 0
        self.frame_duration = 5

        self.actions = set()
        self.grounded = True
        self.attacking = False
        self.attack_duration = 5
        self.attack_frame = 0
        self.attack_cool_down = 0
        self.y_velocity = 0
        self.jump_cooldown = 0

    def update(self, world):
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1

        new_x = self.x
        new_y = self.y

        if "left" in self.actions:
            new_x -= self.speed

        if "right" in self.actions:
            new_x += self.speed

        if new_x > self.x:
            if(self.sprites != self.walking_sprites):
                self.animation_tick = self.frame_duration
                self.sprites = self.walking_sprites
            if(self.direction == "left"):
                self.animation_tick = self.frame_duration
                self.direction = "right"
            else:
                self.animation_tick = (self.animation_tick + 1) % (len(self.sprites) * self.frame_duration)
        elif new_x < self.x:
            if(self.sprites != self.walking_sprites):
                self.animation_tick = self.frame_duration
                self.sprites = self.walking_sprites
            if(self.direction == "right"):
                self.animation_tick = self.frame_duration
                self.direction = "left"
            else:
                self.animation_tick = (self.animation_tick + 1) % (len(self.sprites) * self.frame_duration)
        else:
            self.sprites = self.idle_sprites
            self.animation_tick = 0

        if "jump" in self.actions and self.grounded == True and self.jump_cooldown == 0:
            self.grounded = False
            self.y_velocity = -8

        if self.attack_cool_down > 0:
            self.attack_cool_down -= 1

        if "attack" in self.actions:
            self.attacking = True
            self.attack_frame = 0
            self.attack_cool_down = 10

            # play attack sound
            world.play_attack_sound()

            if(self.direction == "right"):
                for obj in world.active_objects:
                    if(obj.x > self.x and obj.x < self.x + 100 and obj.y > self.y - 50 and obj.y < self.y + 50):
                        if(hasattr(obj, "get_bitten")):
                            obj.get_bitten(world)

            if(self.direction == "left"):
                for obj in world.active_objects:
                    if(obj.x < self.x and obj.x > self.x - 100 and obj.y > self.y - 50 and obj.y < self.y + 50):
                        if(hasattr(obj, "get_bitten")):
                            obj.get_bitten(world)


        if self.grounded == False:
            self.y_velocity += config.GRAVITY
            new_y += self.y_velocity

        self.x = new_x
        self.y = new_y

        self.x = clamp(new_x, 0, config.GAME_WIDTH - self.width/2)
        self.y = clamp(new_y, 0, config.GAME_HEIGHT - self.height/2)

        # Check for collisions
        fall(self, world)

        self.actions.clear()

    def draw(self, screen):
        image = self.sprites[int(self.animation_tick/self.frame_duration)]

        if self.attacking:
            if self.attack_frame < self.attack_duration:
                sprite_index = int((self.attack_frame / self.attack_duration) * len(self.attack_sprites))
                image = self.attack_sprites[sprite_index]
                self.attack_frame += 1
            else:
                self.attack_frame = 0
                self.attacking = False

        image = pygame.transform.scale(image, (self.width, self.height))

        if self.direction == "left":
            image = pygame.transform.flip(image, True, False)

        screen.blit(image, (self.x-self.width/2, self.y-self.height/2))
        
        if config.DEBUG:
            pygame.draw.rect(screen, (255, 0, 0), (self.x-self.width/2, self.y-self.height/2, self.width, self.height), 2)


