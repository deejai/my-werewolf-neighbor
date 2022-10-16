import pygame

import config
from utilities import clamp, fall
from gameobjects.base import GameObject

player_sprite_set_config = {
    "humanform": {
        "idle": {
            "spritesheet": "humanform_walk.png",
            "num_frames": 1,
            "cell_dimensions": (16, 32),
        },
        "walk": {
            "spritesheet": "humanform_walk.png",
            "num_frames": 4,
            "cell_dimensions": (16, 32),
        },
        "interrupt": {
            "spritesheet": "humanform_interrupt.png",
            "num_frames": 4,
            "cell_dimensions": (16, 32),
        }
    },

    "wolfform": {
        "idle": {
            "spritesheet": "werewolf_walk.png",
            "num_frames": 1,
            "cell_dimensions": (32, 32),
        },
        "walk": {
            "spritesheet": "werewolf_walk.png",
            "num_frames": 6,
            "cell_dimensions": (32, 32),
        },
        "attack": {
            "spritesheet": "werewolf_attack.png",
            "num_frames": 5,
            "cell_dimensions": (32, 32),
        }
    }
}

class Player(GameObject):
    def __init__(self):
        super().__init__(64, 64)
        self.sprite_index = 0
        self.speed = 5
        self.direction = "right"

        self.hp = 100

        self.sprite_sets = {}

        for form in player_sprite_set_config:
            self.sprite_sets[form] = {}
            for state in player_sprite_set_config[form]:
                print(f"Loading {form} {state} sprites")
                self.sprite_sets[form][state] = []
                sprite_sheet = pygame.image.load(config.ROOT_DIR + "assets/sprites/" + player_sprite_set_config[form][state]["spritesheet"])
                dimensions = player_sprite_set_config[form][state]["cell_dimensions"]
                for i in range(0, player_sprite_set_config[form][state]["num_frames"]):
                    sprite = sprite_sheet.subsurface((i * dimensions[0], 0, dimensions[0], dimensions[1]))
                    self.sprite_sets[form][state].append(sprite)

        self.form = "wolfform"

        self.animation_tick = 0
        self.frame_duration = 5

        self.actions = set()
        self.grounded = True

        self.attacking = False
        self.attack_duration = 5
        self.attack_frame = 0
        self.attack_cool_down = 0

        self.interrupting = False
        self.interrupt_duration = 5
        self.interrupt_frame = 0
        self.interrupt_cool_down = 0

        self.y_velocity = 0
        self.jump_cooldown = 0

        self.sprites = self.sprite_sets[self.form]["idle"]

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
            if(self.sprites != self.sprite_sets[self.form]["walk"]):
                self.animation_tick = self.frame_duration
                self.sprites = self.sprite_sets[self.form]["walk"]
            if(self.direction == "left"):
                self.animation_tick = self.frame_duration
                self.direction = "right"
            else:
                self.animation_tick = (self.animation_tick + 1) % (len(self.sprites) * self.frame_duration)
        elif new_x < self.x:
            if(self.sprites != self.sprite_sets[self.form]["walk"]):
                self.animation_tick = self.frame_duration
                self.sprites = self.sprite_sets[self.form]["walk"]
            if(self.direction == "right"):
                self.animation_tick = self.frame_duration
                self.direction = "left"
            else:
                self.animation_tick = (self.animation_tick + 1) % (len(self.sprites) * self.frame_duration)
        else:
            self.sprites = self.sprite_sets[self.form]["idle"]
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
                sprite_index = int((self.attack_frame / self.attack_duration) * len(self.sprite_sets["wolfform"]["attack"]))
                image = self.sprite_sets["wolfform"]["attack"][sprite_index]
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

    def reset(self):
        super().reset()

        self.x = 100
        self.y = 200

        self.actions.clear()
