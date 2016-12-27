from math import sin, cos, hypot
import pygame
from constants import DEFAULT_BULLETS_SPEED_PER_FRAME


def dst(x1, y1, x2, y2):
    return hypot(abs(x1-x2), abs(y1-y2))


class Ammo:
    def __init__(self, pos, angle, speed, damage, burst, time_to_live, radius, color, owner):
        self.speed = speed
        self.damage = damage
        self.burst = burst
        self.alive = time_to_live
        self.x, self.y = pos
        self.angle = angle
        self.radius = radius
        self.color = pygame.Color(color)
        self.owner_id = owner
        self.exploded = False

    def get_burst(self):
        return self.burst

    def distance_to_point(self, x, y):
        return ((self.x-x)**2 + (self.y-y)**2)**0.5 - self.radius

    def microtick(self, obstacles, agents):
        boom = self.alive <= 0
        self.x += DEFAULT_BULLETS_SPEED_PER_FRAME*cos(self.angle)
        self.y += DEFAULT_BULLETS_SPEED_PER_FRAME*sin(self.angle)
        if not boom:
            for i in obstacles:
                if i.distance_to_point(self.x, self.y) < self.radius:
                    boom = True
        if not boom:
            for i in agents:
                if i.is_alive and self.owner_id != i.id and dst(self.x, self.y, i.x, i.y) < self.burst + i.radius:
                    boom = True
        # deal damage to everyone who is in burst radius
        missed = True
        if boom:
            self.alive = 0
            for i in agents:
                if i.is_alive and dst(self.x, self.y, i.x, i.y) < self.burst + i.radius:
                    i.take_damage(self.damage, self.owner_id)
                    agents[self.owner_id-1].reward += 1
                    missed = False
            if missed:
                agents[self.owner_id - 1].reward -= 0.25
            self.exploded = True

    def update(self, obstacles, agents):
        self.alive -= 1
        for i in range(self.speed):
            if not self.exploded:
                self.microtick(obstacles, agents)

    def draw(self, screen):
        for i in range(self.speed/2+1):
            pygame.draw.circle(screen,
                               self.color,
                               (int(self.x+cos(self.angle)*self.radius*((-2*i+1)/2)),
                                int(self.y+sin(self.angle)*self.radius*((-2*i+1)/2))),
                               self.radius/2)
            pygame.draw.circle(screen,
                               self.color,
                               (int(self.x-cos(self.angle)*self.radius*((-2*i-1)/2)),
                                int(self.y-sin(self.angle)*self.radius*((-2*i-1)/2))),
                               self.radius/2)


class Bullet(Ammo):
    def __init__(self, pos, angle, owner):
        Ammo.__init__(self, pos, angle, 10, 60, 6, 50, 6, '#ff0000', owner)


class Shell(Ammo):
    def __init__(self, pos, angle, owner):
        Ammo.__init__(self, pos, angle, 5, 40, 6, 200, 6, '#999900', owner)


class Rocket(Ammo):
    def __init__(self, pos, angle, owner):
        Ammo.__init__(self, pos, angle, 1, 150, 20, 200, 10, '#0000ff', owner)