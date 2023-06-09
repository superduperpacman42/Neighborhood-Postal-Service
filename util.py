import math
import os
import sys

import pygame

from constants import *

exe = 0

images = {}
audio = {}


def load_image(name, number=1, angle=0, scale=PIXEL_RATIO, flip=False):
    """ Loads an image or list of images """
    nameF = name
    if flip:
        nameF = name + "Flip"
    if nameF in images:
        return images[nameF]
    if exe:
        path = os.path.join(os.path.dirname(sys.executable), 'images')
    else:
        path = os.path.join(os.path.dirname(__file__), 'images')
    sheet = pygame.image.load(os.path.join(path, name))
    sheet = pygame.transform.scale(sheet, [scale*sheet.get_width(), scale*sheet.get_height()])
    img = []
    w = sheet.get_width()/number
    h = sheet.get_height()
    for i in range(number):
        img.append(sheet.subsurface((w*i, 0, w, h)))
        img[i] = pygame.transform.rotate(img[i], angle)
        img[i] = pygame.transform.flip(img[i], flip, False)
    images[nameF] = img
    return img


def play_music(name):
    """ Plays the given background track """
    if exe:
        path = os.path.join(os.path.dirname(sys.executable), 'audio')
    else:
        path = os.path.join(os.path.dirname(__file__), 'audio')
    pygame.mixer.music.load(os.path.join(path, name))
    pygame.mixer.music.play(-1)


def stop_music():
    """ Stops the current background track """
    pygame.mixer.music.stop()


def set_volume(val):
    """ Scale volume 0 to 1 """
    pygame.mixer.music.set_volume(val)


def play_sound(name, play=True, volume=1):
    """ Plays the given sound effect """
    if name in audio:
        sound = audio[name]
    else:
        if exe:
            path = os.path.join(os.path.dirname(sys.executable), 'audio')
        else:
            path = os.path.join(os.path.dirname(__file__), 'audio')
        sound = pygame.mixer.Sound(os.path.join(path, name))
        sound.set_volume(volume)
        audio[name] = sound
    if play:
        sound.play()


def bounds(pose, w, h):
    return -w / 2 < pose.x < w / 2 and -h / 2 < pose.y < h / 2


def render_money(money):
    c = ["k", "M", "B", "T", "Q"]
    vals = [1e3, 1e6, 1e9, 1e12, 1e15]
    for i in range(4, -1, -1):
        if money >= vals[i]:
            return "$" + (str(money / vals[i])+"000")[:5] + " " + c[i]
    return "$" + str(int(money))


def intersect(line1, line2):
    a, b = line1
    a += (b-a)/10
    b -= (b-a)/10
    c, d = line2
    c += (d-c)/10
    d -= (d-c)/10
    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


def ccw(a, b, c):
    return math.copysign(1, (c.y - a.y) * (b.x - a.x) - (b.y - a.y) * (c.x - a.x))


def center(node, offset=(0, 0), reverse=False):
    if reverse:
        return node[0] - WIDTH / 2 - offset[0], node[1] - HEIGHT / 2 - offset[1]
    return node[0] + WIDTH / 2 + offset[0], node[1] + HEIGHT / 2 + offset[1]


class Pose:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def copy(self):
        return Pose(self.x, self.y)

    def norm(self):
        return math.sqrt(self.x**2 + self.y**2)

    def cw(self):   # assume x right, y down, z into screen
        return Pose(-self.y, self.x)

    def ccw(self):  # assume x right, y down, z into screen
        return Pose(self.y, -self.x)

    def int(self):
        return Pose(int(self.x), int(self.y))

    def round(self):
        return Pose(round(self.x), round(self.y))

    def max(self, p):
        return Pose(max(self.x, p.x), max(self.y, p.y))

    def min(self, p):
        return Pose(min(self.x, p.x), min(self.y, p.y))

    def amax(self, p):
        x = self.x if abs(self.x) > abs(p.x) else p.x
        y = self.y if abs(self.y) > abs(p.y) else p.y
        return Pose(x, y)

    def amin(self, p):
        x = self.x if abs(self.x) < abs(p.x) else p.x
        y = self.y if abs(self.y) < abs(p.y) else p.y
        return Pose(x, y)

    def angle(self):
        return math.degrees(math.atan2(self.y, self.x))

    def __add__(self, p):
        if isinstance(p, Pose):
            return Pose(self.x + p.x, self.y + p.y)
        else:
            return Pose(self.x + p[0], self.y + p[1])

    def __radd__(self, p):
        return Pose(self.x + p[0], self.y + p[1])

    def __sub__(self, p):
        if isinstance(p, Pose):
            return Pose(self.x - p.x, self.y - p.y)
        else:
            return Pose(self.x - p[0], self.y - p[1])

    def __rsub__(self, p):
        return Pose(self.x - p[0], self.y - p[1])

    def __mul__(self, c):
        return Pose(c*self.x, c*self.y)

    def __rmul__(self, c):
        return self*c

    def __truediv__(self, c):
        return Pose(self.x/c, self.y/c)

    def __rtruediv__(self, c):
        return Pose(c/self.x, c/self.y)

    def __neg__(self):
        return Pose(-self.x, -self.y)

    def __pow__(self, c):
        return Pose(self.x**c, self.y**c)

    def __floordiv__(self, c):
        return Pose(self.x//c, self.y//c)

    def __invert__(self):   # get unit vector using ~
        n = self.norm()
        return Pose(self.x/n, self.y/n)

    def __abs__(self):
        return Pose(abs(self.x), abs(self.y))

    def __matmul__(self, p):    # get dot product using @
        if isinstance(p, Pose):
            return self.x*p.x + self.y*p.y
        else:
            return self.x*p[0] + self.y*p[1]

    def __rmatmul__(self, p):   # get dot product using @
        return self.x*p[0] + self.y*p[1]

    def __xor__(self, p):       # get cross product using ^
        if isinstance(p, Pose):
            return self.x*p.y - self.y*p.x
        else:
            return self.x*p[1] - self.y*p[0]

    def __rxor__(self, p):      # get cross product using ^
        return self.x*p[1] - self.y*p[0]

    def __eq__(self, p):
        if isinstance(p, Pose):
            return self.x == p.x and self.y == p.y
        else:
            return self.x == p[0] and self.y == p[1]

    def __req__(self, p):
        return self.x == p[0] and self.y == p[1]

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __hash__(self):
        return hash((self.x, self.y))

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, item):
        if not item:
            return self.x
        return self.y

    def dist_from_line(self, start, end):
        if not isinstance(start, Pose):
            start = Pose(*start)
        d = (start - end).norm()
        if d == 0:
            return (start - self).norm()
        t = max(0, min(1, (self - start) @ (end - start) / d**2))
        p = start + t * (end - start)
        return (p - self).norm()
