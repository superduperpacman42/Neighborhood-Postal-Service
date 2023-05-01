import pygame.draw

from button import Button, CustomButton
from courier import Courier
from floater import Floater
from graph import Graph
from upgrades import *
from util import *


class Game:

    def reset(self):
        """ Resets the game state """
        self.t = 0
        self.map = 0
        self.pause = False
        self.money = 0
        self.approx_money = 0
        self.sound_time = 0
        self.deliveries = 0
        self.maps = [Graph(), Graph(), Graph(), Graph()]
        self.maps[0].generate_houses()
        self.maps[1].generate_cities()
        self.maps[2].generate_world()
        self.maps[3].generate_world()
        self.right_slide = 0
        self.selected = None
        self.max_map = 0
        self.messages = []
        self.messages = [["Welcome to your new job in the postal service!", 3],
                         ["Left-click on a node to walk there", 3],
                         ["Hold shift to select multiple nodes in a row", 3],
                         ["A yellow node indicates the house is expecting a package", 3],
                         ["Once you are out of packages,", 2],
                         ["You will automatically return to the post office for more", 3],
                         ["Good luck!", 3]]

        self.stats["Player"] = {"Speed": 0.1, "Capacity": 1, "Demand": 0.5, "Profit": 1, "Fly": False}
        self.stats["Mailman"] = {"Speed": 0.1, "Capacity": 1, "Fly": False}
        self.stats["Trucker"] = {"Speed": 0.6, "Capacity": 24, "Fly": False}
        self.stats["Pilot"] = {"Speed": 10, "Capacity": 288, "Fly": True}

        self.player = [Courier("Player", self.stats["Player"], self.maps[0]),
                       Courier("Player", self.stats["Player"], self.maps[1]),
                       Courier("Player", self.stats["Player"], self.maps[2])]
        self.groups = [[p] for p in self.player]

        self.upgrades["vehicle"] = [u for u in vehicle]
        self.upgrades["special"] = [u for u in special]
        self.upgrades["mailman"] = copy_upgrade(mailman[0])
        self.floater = ["Letter", "Boxes", "Boxes", "Boxes"]
        self.buttons_left = []
        self.buttons_right = []
        self.floaters = []
        self.buttons_right.append(CustomButton(self, "Zoom In", ("Zoom In",), (), 0, 20, (SIDE_PANEL-3)/2, centered=True))
        self.buttons_right.append(CustomButton(self, "Zoom Out", ("Zoom Out",), (), (SIDE_PANEL-3)/2, 20, (SIDE_PANEL-3)/2, centered=True))

    def ui(self, surface, dt):
        """ Draws the user interface overlay """
        self.update_upgrades()

        left = pygame.Surface((SIDE_PANEL, HEIGHT))
        right = pygame.Surface((SIDE_PANEL, HEIGHT))
        left.fill((153, 153, 153))
        pygame.draw.rect(left, (0, 0, 0), (SIDE_PANEL-3, 0, 3, HEIGHT))
        right.fill((153, 153, 153))
        pygame.draw.rect(right, (0, 0, 0), (0, 0, 3, HEIGHT))

        pygame.draw.rect(left, (0, 0, 0), (10, 10, SIDE_PANEL-23, 80))
        pygame.draw.rect(left, (61, 73, 63), (12, 12, SIDE_PANEL-27, 76))
        score = self.score_font.render(render_money(self.approx_money), True, (224, 224, 224))
        left.blit(score, (20, 20))

        button_speed = 1
        if len(self.buttons_left):
            if self.buttons_left[0].y > 100:
                self.buttons_left[0].y -= dt*button_speed
                if self.buttons_left[0].y < 100:
                    self.buttons_left[0].y = 100
            for b1, b2 in zip(self.buttons_left[:-1], self.buttons_left[1:]):
                if b2.y > b1.y + b1.h:
                    b2.y -= dt*button_speed
                    if b2.y < b1.y + b1.h:
                        b2.y = b1.y + b1.h
        if len(self.buttons_right):
            if self.buttons_right[0].y > 20:
                self.buttons_right[0].y -= dt*button_speed
                if self.buttons_right[0].y < 20:
                    self.buttons_right[0].y = 20
            for b1, b2 in zip(self.buttons_right[:-1], self.buttons_right[1:]):
                if b2.y > b1.y + b1.h:
                    b2.y -= dt*button_speed
                    if b2.y < b1.y + b1.h:
                        b2.y = b1.y + b1.h
        for button in self.buttons_left:
            button.draw(left, self.money)
            if button.purchased:
                button.fade += 10*dt/1000
                if button.fade >= 1:
                    self.buttons_left.remove(button)
        button_states = {"Zoom In": self.map > 0, "Zoom Out": self.map < self.max_map, "Build": False}
        for button in self.buttons_right:
            button.draw(right, button_states[button.name] if isinstance(button, CustomButton) else self.money)
            if button.purchased:
                button.fade += 10*dt/1000
                if button.fade >= 1:
                    self.buttons_right.remove(button)

        surface.blit(left, (0, 0))
        if self.max_map:
            if self.right_slide < SIDE_PANEL:
                self.right_slide += 3*dt/1000 * SIDE_PANEL
            if self.right_slide > SIDE_PANEL:
                self.right_slide = SIDE_PANEL
            surface.blit(right, (WIDTH - self.right_slide, 0))

        if len(self.messages):
            h = 60
            pygame.draw.rect(surface, (0, 0, 0), (SIDE_PANEL+20, HEIGHT - h - 20, WIDTH - 2*SIDE_PANEL - 40, h))
            pygame.draw.rect(surface, (61, 73, 63), (SIDE_PANEL+20+3, HEIGHT - h - 20 +3, WIDTH - 2*SIDE_PANEL - 40 - 6, h - 6))
            text = self.title_font.render(self.messages[0][0], True, (255, 255, 255))
            surface.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT - h))
            self.messages[0][1] -= dt/1000
            if self.messages[0][1] <= 0:
                self.messages = self.messages[1:]

    def update_upgrades(self):
        for t in self.upgrades:
            if t in parallel_types:
                for u in self.upgrades[t]:
                    if u[1] <= self.money * 2 or u[1] <= self.money + 4:
                        if not len(self.buttons_left):
                            h = HEIGHT
                        else:
                            h = max(HEIGHT, self.buttons_left[-1].h + self.buttons_left[-1].y)
                        if h > HEIGHT:
                            return
                        self.upgrades[t].remove(u)
                        b = Button(self, u, t, 0, h)
                        self.buttons_left.append(b)
            else:
                none = True
                for b in self.buttons_left:
                    if b.category == t:
                        none = False
                        break
                if none and len(self.upgrades[t]):
                    u = self.upgrades[t][0]
                    if u[1] < self.money * 2 or u[1] <= self.money + 4 or u[0] == "Launch Space Colony":
                        if not len(self.buttons_left):
                            h = HEIGHT
                        else:
                            h = max(HEIGHT, self.buttons_left[-1].h + self.buttons_left[-1].y)
                        if h > HEIGHT:
                            return
                        self.upgrades[t].remove(u)
                        b = Button(self, u, t, 0, h)
                        self.buttons_left.append(b)

    def update(self, dt, keys):
        """ Updates the game by a timestep and redraws graphics """
        # print(self.stats["Player"])
        self.sound_time += dt/1000
        self.t += dt
        self.shift = keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT]
        deliveries = self.deliveries
        if self.money > self.approx_money:
            self.approx_money += max(1, int(self.money*dt/1000))
            self.approx_money = min(self.approx_money, self.money)
        if self.approx_money > self.money:
            self.approx_money -= max(1, int(self.approx_money * dt / 1000))
            self.approx_money = max(self.approx_money, self.money)

        surface = pygame.Surface((WIDTH, HEIGHT))
        surface.fill((67, 124, 67))

        for i in range(self.max_map+1):
            self.maps[i].update(dt, self.stats["Player"]["Demand"])
            if i == self.map:
                self.maps[i].draw(surface, self.t, self.selected)
            for courier in self.groups[i]:
                packages = courier.update(self.maps[i], dt)
                self.money += packages * self.stats["Player"]["Profit"] * self.maps[i].stats_scale["Profit"]
                if packages:
                    if i == self.map:
                        if courier.name == "Player":
                            play_sound("Delivery.wav", volume=0.5)
                        elif self.sound_time > 0.05:
                            play_sound("EmployeeDelivery.wav", volume=0.2)
                            self.sound_time = 0
                if packages and i == self.map:
                    self.floaters.append(Floater(self.floater[i], courier.pos))
                self.deliveries += packages
                if i == self.map and not courier == self.player[i]:
                    courier.draw(surface, self.t)
            for floater in self.floaters:
                if floater.update(surface, dt):
                    self.floaters.remove(floater)
        self.player[self.map].draw(surface, self.t)
        self.ui(surface, dt)
        self.screen.blit(surface, (0, 0))

    def key_pressed(self, key):
        """ Respond to a key press event """
        if key == pygame.K_RETURN:
            pass
        if key == pygame.K_ESCAPE:
            self.player[self.map].goals = [(0, 0)]
            self.player[self.map].highlight_path(self.maps[self.map])
            self.selected = None

    def mouse_pressed(self, pos, button):
        if button == 1:     # Mouse left
            if pos[0] < SIDE_PANEL:
                for button in self.buttons_left:
                    b = button.bounds()
                    if b[0] <= pos[0] <= b[2] and b[1] <= pos[1] <= b[3]:
                        u = button.upgrade
                        if u[1] > self.money:
                            play_sound("Broke.wav")
                            return
                        play_sound("Upgrade.wav")
                        self.money -= u[1]
                        button.purchased = True
                        if u[0] == "Play Again":
                            self.reset()
                            return
                        for a in u[2]:
                            if a == "Employee":
                                level = u[2][a]
                                types = ["Mailman", "Trucker", "Pilot"]
                                self.groups[level].append(Courier(types[level], self.stats[types[level]], self.maps[level]))
                            elif "Employee" in a:
                                if "Mailmen" in u[0]:
                                    self.stats["Mailman"][a[9:]] *= 1 + u[2][a] / 100
                                elif "Truckers" in u[0]:
                                    self.stats["Trucker"][a[9:]] *= 1 + u[2][a] / 100
                                elif "Pilots" in u[0]:
                                    self.stats["Pilot"][a[9:]] *= 1 + u[2][a] / 100
                            else:
                                self.stats["Player"][a] *= 1 + u[2][a]/100
                            if len(u) >= 4:
                                if u[3]:
                                    for player in self.player:
                                        player.image = load_image(u[3] + ".png")[0]
                            if len(u) >= 5:
                                self.floater[0] = u[4]
                        if u[0] == "Hire Mailman":
                            self.upgrades["mailman_upgrade"] = copy_upgrade(mailman[1], 3, 2)
                        if u[0] == "Buy Truck":
                            self.max_map += 1
                            self.messages.append(["Zoom out to expand your operations!", 3])
                            self.messages.append(["Right-click on a road or city to see available upgrades", 3])
                            self.upgrades["trucker"] = copy_upgrade(trucker[0])
                        if u[0] == "Hire Trucker":
                            self.upgrades["trucker_upgrade"] = copy_upgrade(trucker[1], 3, 2)
                        if u[0] == "Buy Plane":
                            self.max_map += 1
                            self.stats["Player"]["Fly"] = True
                            self.upgrades["pilot"] = copy_upgrade(pilot[0])
                        if u[0] == "Hire Pilot":
                            self.upgrades["pilot_upgrade"] = copy_upgrade(pilot[1], 3, 2)
                        if u[0] == "Launch Space Colony":
                            self.messages.append(["Congratulations on reaching the stars!", 3])
                            self.messages.append(["Your shipping empire will soon span the galaxy", 3])
                            self.messages.append(["Thank you for playing", 10000])
                            if not len(self.buttons_left):
                                h = HEIGHT
                            else:
                                h = max(HEIGHT, self.buttons_left[-1].h + self.buttons_left[-1].y)
                            b = Button(self, play_again[0], None, 0, h)
                            self.buttons_left.append(b)
                        return
            elif pos[0] > WIDTH - SIDE_PANEL and self.right_slide == SIDE_PANEL:
                for button in self.buttons_right:
                    b = button.bounds()
                    if b[0] <= pos[0] - WIDTH + SIDE_PANEL <= b[2] and b[1] <= pos[1] <= b[3] and button.enabled:
                        if button.name == "Zoom Out":
                            self.map += 1
                            if self.selected:
                                self.selected = None
                                self.buttons_right[-1].purchased = True
                                self.buttons_right[-1].fade = 1
                            play_sound("Select.wav")
                        elif button.name == "Zoom In":
                            self.map -= 1
                            if self.selected:
                                self.selected = None
                                self.buttons_right[-1].purchased = True
                                self.buttons_right[-1].fade = 1
                            play_sound("Select.wav")
                        else:   # build
                            u = button.upgrade
                            if u[1] > self.money or not u[1]:
                                play_sound("Broke.wav")
                                return
                            play_sound("Upgrade.wav")
                            self.money -= u[1]
                            button.purchased = True
                            button.fade = 1
                            if "Profit" in u[2]:
                                self.stats["Player"]["Profit"] *= 1 + u[2]["Profit"]/100
                            self.maps[self.map].data[self.selected]["level"] += 1
                            self.update_build(self.selected)

                            if u[0] == "Build Spaceport":
                                self.upgrades["space_upgrade"] = [u for u in space_upgrade]
                        return
            else:
                target = self.maps[self.map].click(pos)
                if isinstance(target, Pose):
                    if self.stats["Player"]["Fly"] or self.maps[self.map].search(self.player[self.map].node, target):
                        if self.shift:
                            self.player[self.map].goals += [target]
                        else:
                            self.player[self.map].goals = [target]
                        self.player[self.map].highlight_path(self.maps[self.map])
        elif button == 3:   # Mouse right
            selected = self.maps[self.map].click(pos)
            play_sound("Select.wav")
            if self.selected:
                self.selected = selected
                self.buttons_right[-1].purchased = True
                self.buttons_right[-1].fade = 1
            if selected:
                self.selected = selected
                self.update_build(selected)

    def update_build(self, selected):
        # if not len(self.buttons_right):
        #     h = HEIGHT
        # else:
        #     h = max(HEIGHT, self.buttons_right[-1].h + self.buttons_right[-1].y)
        h = self.buttons_right[0].h + self.buttons_right[0].y

        if self.map == 1:
            if isinstance(selected, Pose):  # city
                if selected == (0, 0):
                    u = capital_upgrade[self.maps[self.map].data[selected]["level"]]
                else:
                    u = city_upgrade[self.maps[self.map].data[selected]["level"]]
            else:  # road
                u = road_upgrade[self.maps[self.map].data[selected]["level"]]
            b = Button(self, u, "Build", 3, h)
        elif self.map == 2:
            if selected == (0, 0):
                u = home_nation_upgrade[self.maps[self.map].data[selected]["level"]]
            else:
                u = nation_upgrade[self.maps[self.map].data[selected]["level"]]
            b = Button(self, u, "Build", 3, h)
        else:
            b = Button(self, upgraded, "Build", 3, h)
        self.buttons_right.append(b)

################################################################################

    def __init__(self, name):
        """ Initialize the game """
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 30'
        pygame.display.set_caption(name)
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        # icon = loadImage("Icon.png", scale=1)[0]
        # icon.set_colorkey((255, 0, 0))
        # pygame.display.set_icon(icon)
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        # playMusic("Taking_the_Scenic_Route.wav")

        self.score_font = pygame.font.SysFont("franklingothicmedium", 50)
        self.title_font = pygame.font.SysFont("franklingothicmedium", 20)
        self.text_font = pygame.font.SysFont("franklingothicmedium", 18)

        self.t = 0
        self.interface = None
        self.pause = False
        self.maps = None
        self.player = None
        self.money = 0
        self.approx_money = 0
        self.deliveries = 0
        self.groups = []
        self.floater = None
        self.map = 0
        self.max_map = 0
        self.shift = False
        self.right_slide = 0
        self.messages = None
        self.selected = None
        self.sound_time = 0
        self.stats = {}
        self.upgrades = {}
        self.buttons_left = []
        self.buttons_right = []
        self.floaters = []

        self.reset()
        self.run()

    def run(self):
        """ Iteratively call update """
        clock = pygame.time.Clock()
        self.pause = False
        while not self.pause:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.key_pressed(event.key)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_pressed(event.pos, event.button)
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
            dt = clock.tick(TIME_STEP)
            self.update(dt, pygame.key.get_pressed())
            pygame.display.update()


if __name__ == '__main__':
    game = Game("Neighborhood Delivery Service")
