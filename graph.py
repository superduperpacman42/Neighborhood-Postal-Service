import random
from queue import PriorityQueue

import pygame.draw

from util import *


class Graph:

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.data = {}
        self.temp_nodes = []
        self.temp_data = {}
        self.offset = (0, 0)
        self.stats_scale = {"Speed": 1, "Capacity": 1, "Demand": 1, "Profit": 1}

        self.goals = []
        self.first_path_nodes = []
        self.later_path_nodes = []
        self.first_path_edges = []
        self.later_path_edges = []
        self.image = None
        self.t = 0

    def search(self, start, goal):
        start = Pose(*start)
        goal = Pose(*goal)
        open_set = PriorityQueue()
        open_set.put(((start - goal).norm(), start))
        parent = {}
        cost2come = {start: 0}
        best_cost = {start: (start - goal).norm()}
        current = None
        while not open_set.empty():
            cost, current = open_set.get()
            if cost > best_cost[current]:
                continue
            if current == goal:
                break
            for edge in self.edges:
                if current in edge:
                    neighbor = edge[0] if current == edge[1] else edge[1]
                    temp_score = cost2come[current] + (current - neighbor).norm() + tiebreak(current, neighbor)
                    if neighbor not in cost2come or temp_score < cost2come[neighbor]:
                        parent[neighbor] = current
                        cost2come[neighbor] = temp_score
                        open_set.put((temp_score + (neighbor - goal).norm(), neighbor))
                        best_cost[neighbor] = temp_score + (neighbor - goal).norm()
        path = None
        if current == goal:
            path = [current]
            while current in parent:
                current = parent[current]
                path = [current] + path
        return path

    def draw(self, surface, t, selected):
        if self.image:
            surface.blit(self.image, (SIDE_PANEL, 0))
        for edge in self.edges:
            if selected and not isinstance(selected, Pose) and edge == selected:
                color = (0, 255, 0)
            elif edge_in(edge, self.first_path_edges):
                color = (255, 0, 0)
            elif edge_in(edge, self.later_path_edges):
                color = (200, 0, 255)
            else:
                color = (50, 50, 50)
            d = 0
            if "level" in self.data[edge] and self.data[edge]["level"] == 0:
                d = 2
                if color == (50, 50, 50):
                    color = (150, 150, 150)
            draw_line(surface, (0, 0, 0), center(edge[0], self.offset), center(edge[1], self.offset), 9-d)
            draw_line(surface, color, center(edge[0], self.offset), center(edge[1], self.offset), 5-d)
        for node in self.nodes:
            if selected and isinstance(selected, Pose) and node == selected:
                color = (0, 255, 0)
            elif len(self.goals) and node == self.goals[0]:
                color = (255, 0, 0)
            elif node in self.goals:
                color = (200, 0, 255)
            elif node in self.first_path_nodes:
                color = (255, 0, 0)
            elif node in self.later_path_nodes:
                color = (200, 0, 255)
            else:
                color = (70, 70, 70)

            d = 0
            if "level" in self.data[node] and self.data[node]["level"] == 0:
                d = 2
                if color == (70, 70, 70):
                    color = (100, 100, 100)
            pygame.draw.circle(surface, (0, 0, 0), center(node, self.offset), 13-d)
            pygame.draw.circle(surface, color, center(node, self.offset), 10-d)
            if node == (0, 0):
                pygame.draw.circle(surface, (0, 0, 0), center(node, self.offset), 18)
                pygame.draw.circle(surface, color, center(node, self.offset), 15)
            if self.data[node]["package"]:
                pygame.draw.circle(surface, (255, 255, 0), center(node, self.offset), 7-d)
            icon = load_image(self.data[node]["icon"]+".png")[0]

            if "houses" in self.data[node]:
                icons = [load_image("House" + str(i) + ".png")[0] for i in self.data[node]["houses"]]

                if self.data[node]["icon"] == "Capital":
                    icons[2] = load_image("PostOffice.png")[0]
                    if int((self.t * 3) % 2):
                        icons[2] = load_image("PostOffice2.png")[0]
                shift = [(-30, 0), (30, 0), (0, 10), (-25, 20), (25, 20)]
                for i, icon in enumerate(icons):
                    offset = (icon.get_width() / 2, icon.get_height() + 35)
                    surface.blit(icon, center(node - offset + shift[i], self.offset))

            else:
                if self.data[node]["icon"] == "PostOffice" and int((self.t*3) % 2):
                    icon = load_image(self.data[node]["icon"] + "2.png")[0]
                if "level" in self.data[node]:  # city
                    offset = (icon.get_width()/2, icon.get_height() + 15)
                else:                           # house
                    offset = (icon.get_width() + 20, icon.get_height() + 10)
                surface.blit(icon, center(node - offset, self.offset))

    def click(self, mouse):
        mouse = Pose(*center(mouse, self.offset, True))
        for node in self.nodes:
            if (node - mouse).norm() < 20:
                return node
        for edge in self.edges:
            if mouse.dist_from_line(edge[0], edge[1]) < 20:
                return edge
        return None

    def add_node(self, pos, **data):
        node = Pose(*pos)
        self.nodes.append(node)
        self.data[node] = data
        return node

    def add_temp_node(self, pos, **data):
        node = Pose(*pos)
        self.temp_nodes.append(node)
        self.temp_data[node] = data
        return node

    def update(self, dt, demand):
        demand *= self.stats_scale["Demand"]
        for node in self.nodes:
            scale = 1
            scales = [1, 2, 4]
            if "level" in self.data[node]:
                scale = scales[self.data[node]["level"]]
            if demand*dt/1000.0/len(self.nodes)*scale > random.random():
                self.data[node]["package"] = True
                self.data[(0, 0)]["package"] = False
        self.t += dt/1000

    def add_edge(self, start, end, **data):
        edge = (Pose(*start), Pose(*end))
        self.edges.append(edge)
        self.data[edge] = data

    def generate_houses(self):
        self.offset = (20, 20)
        w = 3
        h = 3
        scale = 100
        self.nodes = []
        self.edges = []
        self.data = {}
        self.temp_nodes = []
        self.temp_data = {}
        fixed = ((0, 0), (0, 2), (0, -2), (2, 0), (-2, 0), (2, 2), (-3, 3), (3, -3), (-2, -2))
        for x in range(-w, w+1):
            for y in range(-h, h+1):
                if (x, y) == (0, 0):
                    self.add_node((x * scale, y * scale), package=False, icon="PostOffice")
                elif (x, y) in fixed or random.random() > 0.8:
                    self.add_node((x*scale, y*scale), package=False, icon="House" + str(math.ceil(random.random()*12)))
        connected = [False for _ in self.nodes]
        for i, n1 in enumerate(self.nodes):
            for j, n2 in enumerate(self.nodes[i+1:]):
                if n1.x == n2.x:
                    pathable = True
                    for n in self.nodes:
                        if n1.x == n.x and (n1.y < n.y < n2.y or n1.y > n.y > n2.y):
                            pathable = False
                            break
                    if pathable:
                        self.add_long_edge(n1, n2, abs(n1.y - n2.y)/scale, package=False, icon="House" + str(math.ceil(random.random()*12)))
                        connected[i] = True
                        connected[i+j+1] = True
                if n1.y == n2.y:
                    pathable = True
                    for n in self.nodes:
                        if n1.y == n.y and (n1.x < n.x < n2.x or n1.x > n.x > n2.x):
                            pathable = False
                            break
                    if pathable:
                        self.add_long_edge(n1, n2, abs(n1.x - n2.x)/scale, package=False, icon="House" + str(math.ceil(random.random()*12)))
                        connected[i] = True
                        connected[i+j+1] = True
        for n in fixed:
            if not self.search((0, 0), Pose(*n)*scale):
                self.generate_houses()
                return
        nodes = self.nodes[:]
        for i, c in enumerate(connected):
            if not c:
                self.nodes.remove(nodes[i])
                if nodes[i] == (0, 0):
                    self.generate_houses()
                    return
        for node in self.temp_nodes:
            self.add_node(node, **self.temp_data[node])
        if len(self.nodes) < (2*w+1) * (2*h+1) * 0.6:
            self.generate_houses()
            return

    def generate_cities(self):
        self.stats_scale = {"Speed": 1/9, "Capacity": 1/24, "Demand": 1/24, "Profit": 32}
        self.offset = (0, 30)
        w = HEIGHT
        h = HEIGHT
        border = 55
        min_dist = 130
        road_dist = 250
        self.add_node((0, 0), package=False, icon="Capital", level=0,
                      houses=[math.ceil(random.random()*14) for i in range(5)])
        for i in range(200):
            p = Pose(random.random()*(w - 2*border) - w/2 + border,
                     random.random()*(h - 2*border) - h/2 + border)
            add = True
            for node in self.nodes:
                if (p - node).norm() < min_dist:
                    add = False
                    break
            if add:
                self.add_node(p, package=False, icon="City1", level=0,
                              houses=[math.ceil(random.random()*14) for i in range(5)])
            if len(self.nodes) > 20:
                break
        for i, n1 in enumerate(self.nodes):
            for n2 in self.nodes[i+1:]:
                if (n1 - n2).norm() < road_dist:
                    add = True
                    for road in self.edges:
                        if intersect(road, (n1, n2)):
                            add = False
                            break
                    if add:
                        self.add_edge(n1, n2, level=0)

    def add_long_edge(self, n1, n2, n, **data):
        n = round(n)
        d = (n2-n1)/n
        last = n1
        for i in range(1, n):
            new = d * i + n1
            self.add_temp_node(new, **data)
            self.add_edge(last, new)
            last = new
        self.add_edge(last, n2)

    def generate_world(self):
        self.stats_scale = {"Speed": 1/100, "Capacity": 1/288, "Demand": 1/48, "Profit": 2000}
        self.image = load_image("World.png")[0]
        self.add_node((0, 0), level=0, icon="Capital", package=False,
                      houses=[math.ceil(random.random()*14) for i in range(5)])
        nodes = ((504, 107), (459, 263), (338, 210), (426, 379), (313, 604),
                 (577, 671), (741, 661), (885, 654), (863, 503), (890, 280), (854, 125))
        offset = Pose(*center((0, 0), offset=self.offset))
        for node in nodes:
            self.add_node(Pose(*node) - offset, level=0, icon="City1", package=False,
                          houses=[math.ceil(random.random()*14) for i in range(5)])


def draw_line(surface, color, start, end, width):
    start = Pose(*start)
    end = Pose(*end)
    d = width/2 * (start - end)/(start - end).norm()
    d = (-d[1], d[0])
    points = [start + d, start - d, end - d, end + d]
    points = [(p.x, p.y) for p in points]
    pygame.draw.polygon(surface, color, points)


def edge_in(edge, group):
    return edge in group or (edge[1], edge[0]) in group


def tiebreak(n1, n2):
    return n1.x*1e-6 + n1.y*1e-7 + n2.x*1e-8 + n2.y*1e-9
