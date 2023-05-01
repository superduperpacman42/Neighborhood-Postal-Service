import math
import random

import pygame.draw

from util import *


class Courier:

    def __init__(self, name, stats, graph, node=(0, 0)):
        self.node = node
        self.next = node
        self.goals = [node]
        self.pos = node
        self.name = name
        self.cargo = 0
        self.angle = 0
        self.stats = stats
        self.image = load_image(name + ".png")[0]
        self.graph = graph

    def draw(self, surface, t):
        img = pygame.transform.rotate(self.image, self.angle)

        offset = (img.get_width()/2, img.get_height()/2)
        surface.blit(img, center(Pose(*self.pos) - offset, self.graph.offset))
        if self.name == "Player" and self.cargo:
            n = self.stats["Capacity"] * self.graph.stats_scale["Capacity"]
            if n <= 8:
                boxes = min(n, 5)
                w = 10 if n <= 4 else 8
                p0 = Pose(*self.pos) + (-w*min(n, 4)/2, img.get_height()/2+5) + (1, 1)
                for i in range(int(self.cargo)):
                    d = ((i % 4)*w, int(i/4)*w)
                    pygame.draw.rect(surface, (255, 255, 0), (*center(p0 + d, self.graph.offset), w-2, w-2))
            else:
                w = 10
                p0 = Pose(*self.pos) + (-w * 2, img.get_height() / 2 + 5) + (1, 1)
                d = self.cargo/n
                pygame.draw.rect(surface, (255, 255, 0), (*center(p0, self.graph.offset), w*4*d - 2, w - 2))

    def update(self, graph, dt):
        cargo = 0
        d = (Pose(*self.next) - self.pos).norm()
        edge1 = (self.node, self.next)
        edge2 = (self.next, self.node)
        edgelevel = 0
        if not self.stats["Fly"]:
            if edge1 in self.graph.data and "level" in self.graph.data[edge1]:
                edgelevel = self.graph.data[edge1]["level"]
            elif edge2 in self.graph.data and "level" in self.graph.data[edge2]:
                edgelevel = self.graph.data[edge2]["level"]
        edge_speeds = [1, 3, 6]
        edge_speed = edge_speeds[edgelevel]
        speed = self.stats["Speed"] * self.graph.stats_scale["Speed"] * dt * edge_speed
        if d < speed:
            self.pos = self.next
            self.node = self.next
            if graph.data[self.node]["package"]:
                if self.cargo > 0:
                    self.cargo -= 1
                    cargo += 1
                    graph.data[self.node]["package"] = False
                if self.cargo == 0:   # Return home if empty
                    self.goals = [(0, 0)]
            if self.node == (0, 0):                             # Refill cargo if home
                self.cargo = self.stats["Capacity"] * self.graph.stats_scale["Capacity"]
            if self.next == self.goals[0]:                      # Reached current goal
                self.goals = self.goals[1:]
                if self.name == "Player" and not self.goals:    # Return home if out of goals
                    if self.cargo:
                        self.goals = [self.node]
                    else:
                        self.goals = [(0, 0)]
                        if self.stats["Fly"]:
                            self.next = Pose(0, 0)

                if self.name != "Player" and not self.node == (0, 0):   # Add waypoint if not home
                    if self.cargo > 0:            # Find new goal if not empty
                        self.goals = [random.choice(graph.nodes)]
                        if not self.stats["Fly"] or not graph.data[self.goals[0]]["package"]:
                            if not graph.search(self.node, self.goals[0]):
                                self.goals = [Pose(*self.node)]
                    else:
                        self.goals = [(0, 0)]
            else:
                if self.stats["Fly"]:
                    self.next = Pose(*self.goals[0])
                else:
                    path = graph.search(self.node, self.goals[0])
                    self.next = path[1]
            if self.name == "Player":
                self.highlight_path(graph)
        else:
            delta = Pose(*self.next) - self.pos
            self.pos += speed * delta/d
            self.angle = math.degrees(-math.atan2(delta[1], delta[0])) - 90
        if self.name != "Player" and self.node == (0, 0) and self.next == (0, 0):
            self.goals = [random.choice(graph.nodes)]
            if not graph.data[self.goals[0]]["package"]:
                self.goals = [(0, 0)]
            if not (self.stats["Fly"] or graph.search(self.node, self.goals[0])):
                self.goals = [(0, 0)]
        return cargo

    def highlight_path(self, graph):
        graph.goals = self.goals
        graph.first_path_nodes = []
        graph.later_path_nodes = []
        graph.first_path_edges = []
        graph.later_path_edges = []

        if self.stats["Fly"]:
            return

        path = graph.search(self.next, self.goals[0])
        if path[0] != self.node:
            path = [self.node] + path
        # graph.first_path_nodes.append(path[0])
        for i, node in enumerate(path[1:]):
            graph.first_path_nodes.append(node)
            graph.first_path_edges.append((path[i], node))
        for g, goal in enumerate(self.goals[1:]):
            path = graph.search(self.goals[g], goal)
            for i, node in enumerate(path[1:]):
                graph.later_path_nodes.append(node)
                graph.later_path_edges.append((path[i], node))
