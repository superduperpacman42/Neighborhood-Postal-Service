import pygame

from upgrades import render_upgrade
from util import *


class Button:
    def __init__(self, game, upgrade, category, x, y):
        self.x = x
        self.y = y
        self.category = category
        self.upgrade = upgrade
        self.enabled = True
        self.name = None

        self.dy = 5
        self.border = 10
        self.purchased = False
        self.fade = 0

        self.h = self.dy
        title = game.title_font.render(upgrade[0], True, (0, 0, 0))
        self.h += title.get_height() + self.dy
        self.heights = [self.dy, self.h]
        self.lines = [title]
        for a in upgrade[2]:
            line = game.text_font.render(render_upgrade(a, upgrade[2][a]), True, (0, 0, 0))
            self.lines.append(line)
            self.h += line.get_height() + self.dy
            self.heights.append(self.h)
        self.cost_green = game.text_font.render(render_money(upgrade[1]), True, (36, 100, 14))
        self.cost_red = game.text_font.render(render_money(upgrade[1]), True, (150, 0, 0))
        self.h += self.cost_red.get_height() + self.dy + self.border

    def draw(self, surface, money):
        surf = pygame.Surface((SIDE_PANEL, self.h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 0, 0), (self.border, 0,
                                           SIDE_PANEL - 2 * self.border - 3, self.h - self.border),
                         border_radius=5)
        d = 2
        if self.upgrade[1] and money >= self.upgrade[1]:
            pygame.draw.rect(surf, (192, 192, 192), (self.border + d, d,
                                                     SIDE_PANEL - 2 * self.border - 2*d - 3, self.h - self.border - 2*d),
                             border_radius=3)
        else:
            pygame.draw.rect(surf, (124, 124, 124), (self.border + d, d,
                                                     SIDE_PANEL - 2 * self.border - 2*d - 3, self.h - self.border - 2*d),
                             border_radius=3)
        for height, line in zip(self.heights, self.lines):
            surf.blit(line, (self.border + self.dy, height))
        if not self.upgrade[1]:
            pass
        elif money >= self.upgrade[1]:
            surf.blit(self.cost_green, (SIDE_PANEL - self.border - self.dy - self.cost_green.get_width() - 3,
                                        self.heights[-1]))
        else:
            surf.blit(self.cost_red, (SIDE_PANEL - self.border - self.dy - self.cost_red.get_width() - 3,
                                      self.heights[-1]))
        if self.fade:
            surf.set_alpha(int((1 - self.fade)*255))
            surf.convert_alpha()
        surface.blit(surf, (self.x, self.y))

    def bounds(self):
        return (self.x + self.border, self.y + self.border,
                self.x + SIDE_PANEL - self.border, self.y + self.h - self.border)


class CustomButton:
    def __init__(self, game, name, title, text, x, y, w=SIDE_PANEL - 3, h=0, centered=False):
        self.x = x
        self.y = y
        self.w = w
        self.border = 10
        self.name = name
        self.fade = 0
        self.enabled = False
        self.purchased = False
        self.game = game
        self.centered = centered
        self.hmin = h

        self.dy = 5

        self.set_text(title, text)

    def set_text(self, title, text):
        self.h = self.dy
        self.heights = [self.dy]
        self.title = [self.game.title_font.render(t, True, (0, 0, 0)) for t in title]
        self.text = [self.game.text_font.render(t, True, (0, 0, 0)) for t in text]
        for line in self.title:
            self.h += line.get_height() + self.dy
            self.heights.append(self.h)
        for line in self.text:
            self.h += line.get_height() + self.dy
            self.heights.append(self.h)
        self.lines = self.title + self.text
        self.h = max(self.h + self.border, self.hmin)


    def bounds(self):
        return (self.x + self.border, self.y + self.border,
                self.x + self.w - self.border, self.y + self.h - self.border)

    def draw(self, surface, allowed):
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 0, 0), (self.border + 3, 0,
                                           self.w - 2 * self.border, self.h - self.border),
                         border_radius=5)
        d = 2
        if allowed:
            pygame.draw.rect(surf, (192, 192, 192), (self.border + d + 3, d,
                                                     self.w - 2 * self.border - 2 * d,
                                                     self.h - self.border - 2 * d),
                             border_radius=3)
        else:
            pygame.draw.rect(surf, (124, 124, 124), (self.border + d + 3, d,
                                                     self.w - 2 * self.border - 2 * d,
                                                     self.h - self.border - 2 * d),
                             border_radius=3)
        for height, line in zip(self.heights[:-1], self.lines):
            if self.centered:
                surf.blit(line, (3 + self.w/2 - line.get_width()/2, height))
            else:
                surf.blit(line, (self.border + self.dy+3, height))

        if self.fade:
            surf.set_alpha(int((1 - self.fade) * 255))
            surf.convert_alpha()
        surface.blit(surf, (self.x, self.y))
        self.enabled = allowed
