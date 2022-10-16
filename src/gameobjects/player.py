import pygame

import config
from utilities import clamp, fall
from gameobjects.base import GameObject

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


