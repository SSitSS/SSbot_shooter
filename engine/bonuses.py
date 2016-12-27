import pygame

class Bonus:
    def __init__(self, x, y,
                 new_hp=0,
                 new_armor=0,
                 new_ammo=[0,0,0],
                 radius=3,
                 color='#500000'):
        self.x = x
        self.y = y
        self.new_hp = new_hp
        self.new_armor = new_armor
        self.new_ammo = new_ammo
        self.taken = False
        self.radius = radius
        self.color = pygame.Color(color)

    def distance_to_point(self, x, y):
        return ((self.x-x)**2 + (self.y-y)**2)**0.5 - self.radius

    def distance_to_agent(self, agent):
        return self.distance_to_point(agent.x, agent.y)

    def update(self, agents):
        for i in agents:
            if self.distance_to_agent(i) <= i.radius+self.radius:
                i.take_bonus(self.new_hp, self.new_armor, self.new_ammo)
                self.taken = True

    def draw(self, screen):
        pygame.draw.circle(screen,
                           self.color,
                           (self.x, self.y),
                           self.radius)


class BulletsPack(Bonus):
    def __init__(self, pos):
        Bonus.__init__(self, pos[0], pos[1],
                       new_hp=0,
                       new_armor=0,
                       new_ammo=[10, 0, 0],
                       radius=4,
                       color='#b03030')


class ShellsPack(Bonus):
    def __init__(self, pos):
        Bonus.__init__(self, pos[0], pos[1],
                       new_hp=0,
                       new_armor=0,
                       new_ammo=[0, 5, 0],
                       radius=4,
                       color='#909030')


class RocketsPack(Bonus):
    def __init__(self, pos):
        Bonus.__init__(self, pos[0], pos[1],
                       new_hp=0,
                       new_armor=0,
                       new_ammo=[0, 0, 1],
                       radius=4,
                       color='#5050b0')


class Medkit(Bonus):
    def __init__(self, pos):
        Bonus.__init__(self, pos[0], pos[1],
                       new_hp=50,
                       new_armor=0,
                       new_ammo=[0, 0, 0],
                       radius=6,
                       color='#900000')


class Vest(Bonus):
    def __init__(self, pos):
        Bonus.__init__(self, pos[0], pos[1],
                       new_hp=0,
                       new_armor=50,
                       new_ammo=[0, 0, 0],
                       radius=6,
                       color='#006000')


all_bonuses = [BulletsPack, ShellsPack, RocketsPack, Medkit, Vest]