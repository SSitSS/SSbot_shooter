from constants import *
import pygame
from math import sin, cos, pi
from weapons import Pistol, Shotgun, RocketLauncher, MachineGun

agent_keys = ['max_velocity',
              'turn_speed',
              'max_health',
              'max_armor',
              'spawn_point',
              'starting_angle',
              'starter_weapon_pack',
              'starter_ammo_pack',
              'color',
              'radius']

last_id = 0


class BaseAgent:
    def __init__(self,
                 max_velocity,
                 turn_speed,
                 max_health,
                 max_armor,
                 spawn_point=(200, 200),
                 starting_angle=0,
                 starter_weapon_pack=None,
                 starter_ammo_pack=None,
                 color='#303030',
                 radius=10):

        global last_id
        last_id += 1
        self.id = last_id

        # name could be added any time
        self.name = 'John'

        # basic stats
        self.max_v = max_velocity
        self.turn_v = turn_speed
        self.max_hp = max_health
        self.max_arm = max_armor

        # current stats
        self.spawn_angle = starting_angle
        self.angle = self.spawn_angle
        self.vx, self.vy = 0, 0
        self.v = 0
        self.hp = self.max_hp
        self.arm = 0
        self.spawn_point = spawn_point
        self.x, self.y = self.spawn_point

        # weaponary
        self.active_weapon = PISTOL
        self.active_ammo = BULLETS
        self.ammo_needed_to_shoot = 1
        self.weapons = [Pistol(self.id),
                        Shotgun(self.id),
                        RocketLauncher(self.id),
                        MachineGun(self.id)]
        self.ammo = [10, 5, 1]

        self.is_alive = True
        self.killed_by = -1
        self.to_resurrect = -1

        # visualiser options
        self.color = pygame.Color(color)
        self.radius = radius

        # last actions (needed to keep doing something for multiple ticks)
        self.actions = {'to_go_forward': False,
                        'to_go_back': False,
                        'to_go_left': False,
                        'to_go_right': False,
                        'to_turn_left': False,
                        'to_turn_right': False,
                        'to_shoot': False,
                        'to_take_pistol': False,
                        'to_take_shotgun': False,
                        'to_take_rocket_launcher': False,
                        'to_take_machine_gun': False}

        self.mode = 'Undefined'
        self.decision_function = None

        # stats
        self.kills = 0
        self.deaths = 0

        self.reward = 0

    def reset(self):
        self.angle = self.spawn_angle
        self.hp = self.max_hp
        self.arm = 0
        self.x, self.y = self.spawn_point
        self.ammo = [10, 5, 1]
        self.is_alive = True
        self.killed_by = -1
        self.to_resurrect = -1

    def reload(self):
        self.reset()
        self.kills = 0
        self.deaths = 0


    def distance_to_point(self, x, y):
        return ((self.x-x)**2 + (self.y-y)**2)**0.5 - self.radius

    def take_damage(self, amount, dealer):
        """
        When something deals damage to agent, it takes up to half damage by reducing
        it`s armor value and rest lowers his health. If agent dies, this method writes
        about his death to journal.
        """
        to_armor = min(self.arm, amount/2)
        to_hp = amount - to_armor
        self.arm -= to_armor
        self.hp -= to_hp
        if self.hp <= 0:
            print self.name, 'is dead!'
            self.deaths += 1
            self.reward -=1
            if dealer != self.id:
                self.killed_by = dealer
            else:
                self.killed_by = 0
            self.is_alive = False
            self.to_resurrect = RESURRECTION_DELAY

    def draw(self, screen):
        """
        Draws player top-view sprite with current weapon
        """
        #body
        pygame.draw.circle(screen, self.color,
                           (int(self.x), int(self.y)),
                           self.radius)
        #hands
        pygame.draw.circle(screen, self.color,
                           (int(self.x+self.radius*cos(self.angle+pi/3)),
                            int(self.y+self.radius*sin(self.angle+pi/3))),
                           self.radius/3)
        pygame.draw.circle(screen, self.color,
                           (int(self.x+self.radius*cos(self.angle-pi/3)),
                            int(self.y+self.radius*sin(self.angle-pi/3))),
                           self.radius/3)
        self.weapons[self.active_weapon].draw(screen, pos=(self.x+self.radius*cos(self.angle),
                                                           self.y+self.radius*sin(self.angle)),
                                              angle=self.angle)

    def think(self, observation):
        pass

    def observe(self, observation, reward):
        pass

    def update(self, obstacles):
        """
        Applying actions
        """
        self.reward = 0.1

        for wpn in self.weapons:
            wpn.update()

        if self.actions['to_turn_left'] and not self.actions['to_turn_right']:
            self.angle -= self.turn_v

        if self.actions['to_turn_right'] and not self.actions['to_turn_left']:
            self.angle += self.turn_v

        new_x, new_y = self.x, self.y
        if self.actions['to_go_forward'] and not self.actions['to_go_back']:
            new_x += self.max_v*cos(self.angle)
            new_y += self.max_v*sin(self.angle)

        if self.actions['to_go_back'] and not self.actions['to_go_forward']:
            new_x -= self.max_v*cos(self.angle)/2
            new_y -= self.max_v*sin(self.angle)/2

        if self.actions['to_go_right'] and not self.actions['to_go_left']:
            new_x += self.max_v*cos(self.angle+pi/2)/2
            new_y += self.max_v*sin(self.angle+pi/2)/2

        if self.actions['to_go_left'] and not self.actions['to_go_right']:
            new_x -= self.max_v*cos(self.angle+pi/2)/2
            new_y -= self.max_v*sin(self.angle+pi/2)/2

        collides = False
        for obs in obstacles:
            if obs.distance_to_point(new_x, new_y) < self.radius:
                collides = True
                break

        if not collides:
            self.x, self.y = new_x, new_y

        if self.actions['to_take_pistol']:
            self.active_weapon = PISTOL
            self.active_ammo = BULLETS
        if self.actions['to_take_shotgun']:
            self.active_weapon = SHOTGUN
            self.active_ammo = SHELLS
        if self.actions['to_take_rocket_launcher']:
            self.active_weapon = ROCKET_LAUNCHER
            self.active_ammo = ROCKETS
        if self.actions['to_take_machine_gun']:
            self.active_weapon = MACHINE_GUN
            self.active_ammo = BULLETS
        self.ammo_needed_to_shoot = self.weapons[self.active_weapon].per_shot

        if self.actions['to_shoot'] and self.ammo[self.active_ammo] >= self.ammo_needed_to_shoot:
            if self.weapons[self.active_weapon].cooling == 0:
                self.ammo[self.active_ammo] -= self.ammo_needed_to_shoot
            return self.weapons[self.active_weapon].shoot((self.x+self.radius*cos(self.angle),
                                                           self.y+self.radius*sin(self.angle)), angle=self.angle)
        else:
            if self.ammo[self.active_ammo] < self.ammo_needed_to_shoot:
                self.reward -= 0.25
            return []

    def take_bonus(self,
                   new_hp=0,
                   new_armor=0,
                   new_ammo=[0, 0, 0]):
        self.reward += 0.1
        self.hp = min(new_hp+self.hp, self.max_hp)
        self.arm = min(new_armor+self.arm, self.max_arm)
        for i in range(3):
            self.ammo[i] += new_ammo[i]
