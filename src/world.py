import os
import pygame
import random

import config
from gameobjects.base import Platform
from gameobjects.citizen import Citizen
from gameobjects.scenery import Scenery, Building
from gameobjects.player import Player

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

        self.citizens = []
        self.citizens.append(self.objects["citizen_miguel"])
        self.citizens.append(self.objects["citizen_mark"])
        self.citizens.append(Citizen("assets/sprites/citizen_miguel.png", 64, 32))
        self.citizens.append(Citizen("assets/sprites/citizen_miguel.png", 32, 64))
        self.citizens.append(Citizen("assets/sprites/citizen_miguel.png", 16, 32))
        self.citizens.append(Citizen("assets/sprites/citizen_miguel.png", 32, 16))

        self.player = Player()

        self.active_objects = [self.player]

        self.phase = "night"

        self.next_channel = 1

    def reset_objects(self):
        for obj in self.active_objects:
            obj.reset()

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
        self.reset_objects()
        self.phase = "night"

        pygame.mixer.Channel(1).stop()
        pygame.mixer.Channel(2).stop()
        pygame.mixer.Channel(3).stop()

        self.change_music(config.ROOT_DIR + "assets/audio/bg_night.wav", 0.1)

        self.active_objects = [self.player]

        self.populate("moon", 100, 100)
        self.populate("church", 320, config.GAME_HEIGHT-71-ground_level)
        self.populate("house1", 100, config.GAME_HEIGHT-48-ground_level)
        self.populate("house2", 550, config.GAME_HEIGHT-48-ground_level)

        self.populate("grass", config.GAME_WIDTH/2, config.GAME_HEIGHT-ground_level/2)
        self.populate("dirt", config.GAME_WIDTH/2, config.GAME_HEIGHT-16-ground_level)

        self.populate("night_sky", config.GAME_WIDTH/2, config.GAME_HEIGHT/2)

        self.player.x = 100
        self.player.y = ground_level-32

        self.citizen_scared_sounds = []
        # add each file in the assets/sounds/citizen_scared folder to the list
        folder = config.ROOT_DIR + "assets/audio/citizen_scared/"
        for file in os.listdir(folder):
            if file.endswith(".wav"):
                sound = pygame.mixer.Sound(folder + file)
                sound.set_volume(0.3)
                self.citizen_scared_sounds.append(sound)

        self.last_citizen_scared_sound = None

        self.citizen_gossip_sounds = []
        # add each file in the assets/sounds/citizen_gossip folder to the list
        folder = config.ROOT_DIR + "assets/audio/citizen_gossip/"
        for file in os.listdir(folder):
            if file.endswith(".wav"):
                sound = pygame.mixer.Sound(folder + file)
                sound.set_volume(0.8)
                self.citizen_gossip_sounds.append(sound)

        self.last_citizen_gossip_sound = None

    def start_day(self):
        self.reset_objects()
        self.phase = "day"

        pygame.mixer.Channel(1).stop()
        pygame.mixer.Channel(2).stop()
        pygame.mixer.Channel(3).stop()

        self.change_music(config.ROOT_DIR + "assets/audio/bg_day.wav", 0.1)

        self.active_objects = [self.player]

        self.populate("church", 320, config.GAME_HEIGHT-71-ground_level)
        self.populate("house1", 100, config.GAME_HEIGHT-48-ground_level)
        self.populate("house2", 550, config.GAME_HEIGHT-48-ground_level)

        self.populate("grass", config.GAME_WIDTH/2, config.GAME_HEIGHT-ground_level/2)
        self.populate("dirt", config.GAME_WIDTH/2, config.GAME_HEIGHT-16-ground_level)

        self.populate("day_sky", config.GAME_WIDTH/2, config.GAME_HEIGHT/2)

        self.player.x = 100
        self.player.y = ground_level-32

    def play_on_next_channel(self, sound):
        pygame.mixer.Channel(self.next_channel).play(sound)
        self.next_channel += 1
        if self.next_channel > 3:
            self.next_channel = 1

    def play_citizen_scared_sound(self):
        sound = random.choice([s for s in self.citizen_scared_sounds if s != self.last_citizen_scared_sound])
        self.last_citizen_scared_sound = sound
        sound.set_volume(0.5)
        self.play_on_next_channel(sound)

    def play_citizen_gossip_sound(self):
        sound = random.choice([s for s in self.citizen_gossip_sounds if s != self.last_citizen_gossip_sound])
        self.last_citizen_gossip_sound = sound
        sound.set_volume(0.5)
        self.play_on_next_channel(sound)

    def play_attack_sound(self):
        sound = pygame.mixer.Sound(config.ROOT_DIR + "assets/audio/bite.wav")
        sound.set_volume(0.3)
        self.play_on_next_channel(sound)

    def change_music(self, filepath, volume=1.0):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=-1, start=0.0, fade_ms=1000)
