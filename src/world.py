import os
import pygame
import random

import config
from gameobjects.base import Platform
from gameobjects.citizen import Citizen
from gameobjects.scenery import Scenery, Building
from gameobjects.player import Player
from gameobjects.detective import Detective
from gameobjects.hunter import Hunter

ground_level = 150

class World:
    def __init__(self):
        self.objects = {}

        self.objects["citizen_miguel"] = Citizen("assets/sprites/citizen_miguel.png", 32, 32)
        self.objects["citizen_mark"] = Citizen("assets/sprites/citizen_mark.png", 32, 32)
        self.objects["grass"] = Platform("assets/sprites/grass.png", config.GAME_WIDTH, ground_level)
        self.objects["dirt"] = Scenery("assets/sprites/dirt.png", config.GAME_WIDTH, 32)
        self.objects["moon"] = Scenery("assets/sprites/moon.png")
        self.objects["church"] = Building("assets/sprites/church.png")
        self.objects["house1"] = Building("assets/sprites/house_brown.png")
        self.objects["house2"] = Building("assets/sprites/house_brown.png")
        self.objects["night_sky"] = Scenery("assets/sprites/night_sky.png", 640, 480)
        self.objects["day_sky"] = Scenery("assets/sprites/day_sky.png", 640, 480)
        self.objects["detective"] = Detective()

        self.citizens = []
        self.citizens.append(self.objects["citizen_miguel"])
        self.citizens.append(self.objects["citizen_mark"])
        for i in range(8):
            self.citizens.append(Citizen("assets/sprites/rando_citizen_male.png", 32, 32))
        
        for i in range(8):
            self.citizens.append(Citizen("assets/sprites/rando_citizen_female.png", 32, 32))

        self.player = Player()

        self.active_objects = [self.player]

        self.phase = "night"
        self.phase_timer = 0

        self.next_channel = 1

        self.suspicion = 0
        self.investigation = 0

        self.citizen_scared_sounds = []
        folder = config.ROOT_DIR + "assets/audio/citizen_scared/"
        for file in os.listdir(folder):
            if file.endswith(".wav"):
                sound = pygame.mixer.Sound(folder + file)
                sound.set_volume(0.3)
                self.citizen_scared_sounds.append(sound)

        self.last_citizen_scared_sound = None

        self.citizen_gossip_sounds = []
        folder = config.ROOT_DIR + "assets/audio/citizen_gossip/"
        for file in os.listdir(folder):
            if file.endswith(".wav"):
                sound = pygame.mixer.Sound(folder + file)
                sound.set_volume(0.5)
                self.citizen_gossip_sounds.append(sound)

        self.last_citizen_gossip_sound = None

        self.detective_notice_sounds = []
        folder = config.ROOT_DIR + "assets/audio/detective_notice/"
        for file in os.listdir(folder):
            if file.endswith(".wav"):
                sound = pygame.mixer.Sound(folder + file)
                sound.set_volume(0.5)
                self.detective_notice_sounds.append(sound)

        self.last_detective_notice_sound = None

        self.detective_investigate_sounds = []
        folder = config.ROOT_DIR + "assets/audio/detective_investigate/"
        for file in os.listdir(folder):
            if file.endswith(".wav"):
                sound = pygame.mixer.Sound(folder + file)
                sound.set_volume(0.6)
                self.detective_investigate_sounds.append(sound)

        self.last_detective_investigate_sound = None

        self.hunter_taunt_sounds = []
        folder = config.ROOT_DIR + "assets/audio/hunter_taunt/"
        for file in os.listdir(folder):
            if file.endswith(".wav"):
                sound = pygame.mixer.Sound(folder + file)
                sound.set_volume(0.6)
                self.hunter_taunt_sounds.append(sound)

        self.last_hunter_taunt_sound = None

        self.werewolf_hurt_sounds = []
        folder = config.ROOT_DIR + "assets/audio/werewolf_hurt/"
        for file in os.listdir(folder):
            if file.endswith(".wav"):
                sound = pygame.mixer.Sound(folder + file)
                sound.set_volume(0.8)
                self.werewolf_hurt_sounds.append(sound)

        self.last_werewolf_hurt_sound = None

    def reset_citizens(self):
        for citizen in self.citizens:
            citizen.active = False
            citizen.reset()

    def populate(self, key, x, y, first=False):
        obj = self.objects[key]
        obj.x = x
        obj.y = y
        if first:
            self.active_objects.insert(1, obj)
        else:
            self.active_objects.append(obj)
        self.active = True

    def depopulate(self, obj):
        obj.active = False
        self.active_objects.remove(obj)

    def start_night(self):
        self.phase_timer = 0
        self.reset_citizens()
        self.phase = "night"
        self.player.form = "wolfform"
        self.player.width = 64
        self.player.height = 64

        pygame.mixer.Channel(1).stop()
        pygame.mixer.Channel(2).stop()
        pygame.mixer.Channel(3).stop()

        self.change_music(config.ROOT_DIR + "assets/audio/bg_night.wav", 0.1)

        self.active_objects = [self.player]

        self.objects["hunter"] = Hunter()
        self.populate("hunter", 500, config.GAME_HEIGHT-48-ground_level)

        self.populate("moon", 100, 100)
        self.populate("church", 320, config.GAME_HEIGHT-71-ground_level)
        self.populate("house1", 100, config.GAME_HEIGHT-48-ground_level)
        self.populate("house2", 550, config.GAME_HEIGHT-48-ground_level)

        self.populate("grass", config.GAME_WIDTH/2, config.GAME_HEIGHT-ground_level/2)
        self.populate("dirt", config.GAME_WIDTH/2, config.GAME_HEIGHT-16-ground_level)

        self.populate("night_sky", config.GAME_WIDTH/2, config.GAME_HEIGHT/2)

    def start_day(self):
        self.phase_timer = 0
        self.reset_citizens()
        self.phase = "day"
        self.player.form = "humanform"
        self.player.width = 32
        self.player.height = 64

        pygame.mixer.Channel(1).stop()
        pygame.mixer.Channel(2).stop()
        pygame.mixer.Channel(3).stop()

        self.change_music(config.ROOT_DIR + "assets/audio/bg_day.wav", 0.1)

        self.active_objects = [self.player]

        self.objects["detective"] = Detective()
        self.populate("detective", 500, config.GAME_HEIGHT-48-ground_level)

        self.populate("church", 320, config.GAME_HEIGHT-71-ground_level)
        self.populate("house1", 100, config.GAME_HEIGHT-48-ground_level)
        self.populate("house2", 550, config.GAME_HEIGHT-48-ground_level)

        self.populate("grass", config.GAME_WIDTH/2, config.GAME_HEIGHT-ground_level/2)
        self.populate("dirt", config.GAME_WIDTH/2, config.GAME_HEIGHT-16-ground_level)

        self.populate("day_sky", config.GAME_WIDTH/2, config.GAME_HEIGHT/2)

        self.player.x = 100
        self.player.y = ground_level-32

    def game_over(self, reason):
        self.reset_citizens()
        self.phase = "game_over"
        self.player.form = "humanform"
        self.player.width = 32
        self.player.height = 64

        pygame.mixer.Channel(1).stop()
        pygame.mixer.Channel(2).stop()
        pygame.mixer.Channel(3).stop()

        self.change_music(config.ROOT_DIR + "assets/audio/bg_hum.wav", 0.1)

        self.active_objects = [self.player]

        self.populate("grass", config.GAME_WIDTH/2, config.GAME_HEIGHT-ground_level/2)
        self.populate("dirt", config.GAME_WIDTH/2, config.GAME_HEIGHT-16-ground_level)

        self.populate("day_sky", config.GAME_WIDTH/2, config.GAME_HEIGHT/2)

        self.player.x = 100
        self.player.y = ground_level-32

        print("GAME OVER")

    def draw_bars(self, screen):
        # draw health bar
        pygame.draw.rect(screen, (255, 0, 0), (0, 0, config.GAME_WIDTH, 10))
        pygame.draw.rect(screen, (0, 255, 0), (0, 0, int(config.GAME_WIDTH*self.player.hp/100), 10))

        # draw suspicion bar
        pygame.draw.rect(screen, (255, 0, 0), (0, 10, config.GAME_WIDTH, 10))
        pygame.draw.rect(screen, (0, 255, 0), (0, 10, int(config.GAME_WIDTH*self.suspicion/100), 10))

        # draw investigation bar
        pygame.draw.rect(screen, (255, 0, 0), (0, 20, config.GAME_WIDTH, 10))
        pygame.draw.rect(screen, (0, 255, 0), (0, 20, int(config.GAME_WIDTH*self.investigation/100), 10))

        # draw phase timer
        pygame.draw.rect(screen, (255, 0, 0), (0, 30, config.GAME_WIDTH, 10))
        pygame.draw.rect(screen, (0, 255, 0), (0, 30, int(config.GAME_WIDTH*self.phase_timer/config.PHASE_DURATION), 10))

    def play_on_next_channel(self, sound):
        pygame.mixer.Channel(self.next_channel).play(sound)
        self.next_channel += 1
        if self.next_channel > 3:
            self.next_channel = 1

    def play_citizen_scared_sound(self):
        sound = random.choice([s for s in self.citizen_scared_sounds if s != self.last_citizen_scared_sound])
        self.last_citizen_scared_sound = sound
        self.play_on_next_channel(sound)

    def play_citizen_gossip_sound(self):
        sound = random.choice([s for s in self.citizen_gossip_sounds if s != self.last_citizen_gossip_sound])
        self.last_citizen_gossip_sound = sound
        self.play_on_next_channel(sound)

    def play_detective_notice_sound(self):
        sound = random.choice([s for s in self.detective_notice_sounds if s != self.last_detective_notice_sound])
        self.last_detective_notice_sound = sound
        self.play_on_next_channel(sound)

    def play_detective_investigate_sound(self):
        sound = random.choice([s for s in self.detective_investigate_sounds if s != self.last_detective_investigate_sound])
        self.last_detective_investigate_sound = sound
        self.play_on_next_channel(sound)

    def play_attack_sound(self):
        sound = pygame.mixer.Sound(config.ROOT_DIR + "assets/audio/bite.wav")
        self.play_on_next_channel(sound)

    def play_hunter_taunt_sound(self):
        sound = random.choice([s for s in self.hunter_taunt_sounds if s != self.last_hunter_taunt_sound])
        self.last_hunter_taunt_sound = sound
        self.play_on_next_channel(sound)

    def play_gunshot_sound(self):
        sound = pygame.mixer.Sound(config.ROOT_DIR + "assets/audio/shoot.wav")
        self.play_on_next_channel(sound)

    def play_werewolf_hurt_sound(self):
        sound = random.choice([s for s in self.werewolf_hurt_sounds if s != self.last_werewolf_hurt_sound])
        self.last_werewolf_hurt_sound = sound
        self.play_on_next_channel(sound)

    def change_music(self, filepath, volume=1.0):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=-1, start=0.0, fade_ms=1000)
