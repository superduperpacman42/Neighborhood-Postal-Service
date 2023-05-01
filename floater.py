import random

import pygame

from util import *


class Floater:
    def __init__(self, name, origin, time=0.5):
        self.image = load_image(name + ".png")[0]
        self.origin = Pose(*origin) - (20*random.random(), 20*random.random())
        self.time = time
        self.t = 0

    def update(self, surface, dt):
        self.t += dt/1000
        surf = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA)
        surf.blit(self.image, (0, 0))
        surf.set_alpha(int((1 - self.t/self.time) * 255))
        surf.convert_alpha()
        self.origin.y -= 20*dt/1000
        self.origin.x -= 10*dt/1000
        surface.blit(surf, center((self.origin.x - self.image.get_width()/2,
                                   self.origin.y - self.image.get_height()/2)))
        return self.t >= self.time
