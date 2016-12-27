from walls import Column, Wall
from base_agent import *
from default_agents import *
from time import sleep, time
from bonuses import *
import pygame
from math import pi, sin, cos
from random import random, randint
from constants import *
import numpy as np


journal = []

stats_names = ['Pos', 'Name', 'K', 'D', 'K-D', 'K/D', 'HP', 'A', 'B', 'S', 'R']

MAX_SCORE = 50


def get_status_vector(value, max_value, size):
    output = np.zeros(shape=[size], dtype='float16')
    full = int(float(value)/max_value*size)
    for i in range(min(full, size)):
        output[i] = 1
    if full < size:
        output[full] = float(value)/max_value*size - int(float(value)/max_value*size)
    return output


def render_line(screen, lst, x0, y0, clr=pygame.Color('#ffffff')):
    deltas = [0, 32, 80, 24, 24, 32, 40, 32, 32, 32, 32]
    text_color = clr
    bg_color = pygame.Color('#101010')
    font = pygame.font.SysFont('timesnewroman', 16)
    for i in range(len(lst)):
        header = font.render(str(lst[i]), True, text_color, bg_color)
        screen.blit(header, (x0+sum(deltas[:i+1]), y0))


def save_result(stats, path):
    with open(path, 'w') as f:
        lines = ['\t'.join([str(i) for i in line]) for line in stats]
        f.write('\n'.join(lines))


class World:
    def __init__(self, map_name):
        self.name = map_name
        self.width, self.height = 0, 0
        self.obstacles = []
        self.agents = []
        self.bullets = []
        self.bonuses = []
        self.ready = False
        self.background_color = pygame.Color('#101010')
        self.bg = None
        self.stats_bg = None
        self.time = 0
        self.bonus_spawner = []
        self.stats = []

        self.angle_shift = 0.125
        self.rays = 17
        self.critical_distance = 10
        self.layers = 8
        self.vision_range = 300
        self.distance_shift = 20

        self.round = 1
        self.ticks = 0
        self.episode_duration = 1000

    def load(self):
        map_size, map_agents, map_walls, map_columns, map_bonuses = None, None, None, None, None
        exec('from '+self.name+' import map_size, map_agents, map_walls, map_columns, map_bonuses')
        if map_size and map_agents and map_walls and map_columns and map_bonuses:
            map_size[0]+=STATS_WIDTH
            self.width, self.height = map_size
            self.bg = pygame.Surface((self.width-STATS_WIDTH, self.height))
            self.bg.fill(self.background_color)
            self.stats_bg = pygame.Surface((STATS_WIDTH, self.height))
            self.stats_bg.fill(self.background_color)

            for params in map_agents:
                agent_creation = 'self.agents.append('+params[0]+'('
                for key in agent_keys:
                    agent_creation += "params[1]['"+key+"'],"
                agent_creation = agent_creation[:-1]+'))'
                exec agent_creation

            for col in map_columns:
                self.obstacles.append(Column(col[0], col[1], col[2]))

            for wall in map_walls:
                self.obstacles.append(Wall(center_pos=wall[0], width=wall[1], height=wall[2], color=wall[3]))

            for i in range(len(all_bonuses)):
                for bonus in map_bonuses[i]:
                    self.bonus_spawner.append({'self': all_bonuses[i],
                                               'pos': (bonus[0], bonus[1]),
                                               'cooldown': bonus[2],
                                               'spawn_next_in': bonus[2]})

            self.fill_holder()

            self.ready = True
            print 'Loading finished'
        else:
            print 'Loading failed'
            # raise MapLoadingError

    def reset(self):
        for i in self.agents:
            x, y, angle = randint(300, 780), randint(200, 480), random()*6.29
            i.spawn_angle = angle
            i.spawn_point = (x, y)
            i.reload()

    def fill_holder(self):
        self.stats = []
        for agent in self.agents:
            kdr = 1.0
            if agent.deaths:
                kdr = float(agent.kills)/agent.deaths
            line = [1,
                    agent.name,
                    agent.kills,
                    agent.deaths,
                    agent.kills-agent.deaths,
                    kdr,
                    agent.hp,
                    agent.arm,
                    agent.ammo[BULLETS],
                    agent.ammo[SHELLS],
                    agent.ammo[ROCKETS]]
            self.stats.append(line)

    def draw_stats(self, screen):
        global stats_names
        x0, y0 = self.width-STATS_WIDTH, 0
        screen.blit(self.stats_bg, (x0, y0))
        render_line(screen, stats_names, x0, y0)
        pos = 1
        self.stats.sort(key=lambda x: -x[STAT_SCORE])
        for agent_stats in self.stats:
            agent_stats[0] = pos
            for i in self.agents:
                if i.name == agent_stats[1]:
                    clr = i.color
            render_line(screen, agent_stats[:2]+[str(i)[:4] for i in agent_stats[2:]], x0, y0+16*pos, clr)
            pos += 1

    def draw(self, screen):
        screen.blit(self.bg, (0,0))
        for i in self.obstacles:
            i.draw(screen)
        for i in self.bonuses:
            i.draw(screen)
        for i in self.agents:
            if i.is_alive:
                i.draw(screen)
        for i in self.bullets:
            i.draw(screen)
        self.draw_stats(screen)

    def get_all_collisions(self, x, y, r, ai, walls_, enemies_, bonus_medkits_, bonus_vests_,
                           bonus_bullets_, bonus_shells_, bonus_rockets_, flying_bullets_):
        collisions = [False]*8
        walls = [i.distance_to_point(x, y) < r for i in walls_]
        if walls:
            collisions[OBSTACLES_LAYER] = max(walls)
        enemies = [i.distance_to_point(x, y) < r for i in enemies_]
        if enemies:
            collisions[ENEMIES_LAYER] = max(enemies)
        bonus_medkits = [i.distance_to_point(x, y) < r for i in bonus_medkits_]
        if bonus_medkits:
            collisions[MEDKITS_LAYER] = max(bonus_medkits)
        bonus_vests = [i.distance_to_point(x, y) < r for i in bonus_vests_]
        if bonus_vests:
            collisions[VESTS_LAYER] = max(bonus_vests)
        bonus_bullets = [i.distance_to_point(x, y) < r for i in bonus_bullets_]
        if bonus_bullets:
            collisions[BULLETS_LAYER] = max(bonus_bullets)
        bonus_shells = [i.distance_to_point(x, y) < r for i in bonus_shells_]
        if bonus_shells:
            collisions[SHELLS_LAYER] = max(bonus_shells)
        bonus_rockets = [i.distance_to_point(x, y) < r for i in bonus_rockets_]
        if bonus_rockets:
            collisions[ROCKETS_LAYER] = max(bonus_rockets)
        flying_bullets = [i.distance_to_point(x, y) < r for i in flying_bullets_]
        if flying_bullets:
            collisions[MISSILES_LAYER] = max(flying_bullets)
        return collisions

    def get_observation(self, agent_index):
        """
        This method returns what agent with given index can observe.
        TODO: rewrite this code in order to make it fast and readable.
        :param agent_index:
        :return:
        """
        if self.agents[agent_index].name.startswith('Target'):
            return np.zeros(shape=(self.layers+5, self.rays))

        x0 = self.agents[agent_index].x
        y0 = self.agents[agent_index].y
        a0 = self.agents[agent_index].angle

        angles = np.arange(-1, 1.01, self.angle_shift)
        observation = np.zeros(shape=(self.layers+5, self.rays))

        observation[-5] = get_status_vector(self.agents[agent_index].hp, 100, self.rays)
        observation[-4] = get_status_vector(self.agents[agent_index].arm, 100, self.rays)
        observation[-3] = get_status_vector(self.agents[agent_index].ammo[0], 50, self.rays)
        observation[-2] = get_status_vector(self.agents[agent_index].ammo[1], 50, self.rays)
        observation[-1] = get_status_vector(self.agents[agent_index].ammo[2], self.rays, self.rays)

        walls_ = [(i.distance_to_point(x0, y0) < 1.1*self.vision_range) for i in self.obstacles]
        walls = []
        for i in range(len(walls_)):
            if walls_[i]:
                walls.append(self.obstacles[i])

        enemies_ = [(i.id != self.agents[agent_index].id and i.is_alive) for i in self.agents]
        enemies = []
        for i in range(len(enemies_)):
            if enemies_[i]:
                enemies.append(self.agents[i])
        bonus_medkits_ = [(i.new_hp > 0) for i in self.bonuses]
        bonus_medkits = []
        for i in range(len(bonus_medkits_)):
            if bonus_medkits_[i]:
                bonus_medkits.append(self.bonuses[i])
        bonus_vests_ = [(i.new_armor > 0) for i in self.bonuses]
        bonus_vests = []
        for i in range(len(bonus_vests_)):
            if bonus_vests_[i]:
                bonus_vests.append(self.bonuses[i])
        bonus_bullets_ = [(i.new_ammo[BULLETS] > 0) for i in self.bonuses]
        bonus_bullets = []
        for i in range(len(bonus_bullets_)):
            if bonus_bullets_[i]:
                bonus_bullets.append(self.bonuses[i])
        bonus_shells_ = [(i.new_ammo[SHELLS] > 0) for i in self.bonuses]
        bonus_shells = []
        for i in range(len(bonus_shells_)):
            if bonus_shells_[i]:
                bonus_shells.append(self.bonuses[i])
        bonus_rockets_ = [(i.new_ammo[ROCKETS] > 0) for i in self.bonuses]
        bonus_rockets = []
        for i in range(len(bonus_rockets_)):
            if bonus_rockets_[i]:
                bonus_rockets.append(self.bonuses[i])
        flying_bullets_ = [(i.owner_id != self.agents[agent_index].id) for i in self.bullets]
        flying_bullets = []
        for i in range(len(flying_bullets_)):
            if flying_bullets_[i]:
                flying_bullets.append(self.bullets[i])

        for a in range(self.rays):
            for d in range(1, self.vision_range/self.distance_shift):
                px, py = x0+d*self.distance_shift*cos(a0+angles[a]), y0+d*self.distance_shift*sin(a0+angles[a])
                collisions = self.get_all_collisions(px, py, self.critical_distance, self.agents[agent_index].id, walls,
                                                     enemies, bonus_medkits, bonus_vests, bonus_bullets,
                                                     bonus_shells, bonus_rockets, flying_bullets)
                for i in range(self.layers):
                    if collisions[i] and observation[i][a] == 0:
                        observation[i][a] = float(self.vision_range-d*self.distance_shift)/self.vision_range
                if collisions[0]:
                    break
        return observation.transpose()

    def tick(self):
        self.ticks += 1
        start = time()
        self.time += 1

        for bonus in self.bonus_spawner:
            if bonus['spawn_next_in'] > 1:
                bonus['spawn_next_in'] -= 1
            elif bonus['spawn_next_in'] == 1:
                self.bonuses.append(bonus['self'](bonus['pos']))
                bonus['spawn_next_in'] = 0
            elif bonus['spawn_next_in'] == 0:
                taken = True
                for i in self.bonuses:
                    if i.x == bonus['pos'][0] and i.y == bonus['pos'][1]:
                        taken = False
                        break
                if taken:
                    bonus['spawn_next_in'] = bonus['cooldown']

        killers = []
        i = 0
        observations = {i.name:0 for i in self.agents}
        for agent in self.agents:
            agent.reward = 0
        for agent in self.agents:
            if agent.is_alive:
                observations[agent.name] = self.get_observation(i)
                agent.think(observations[agent.name])
                new_bullets = agent.update(self.obstacles)
                self.bullets += new_bullets
            elif agent.to_resurrect:
                agent.to_resurrect -= 1
                if agent.killed_by:
                    killers.append(agent.killed_by)
                    agent.killed_by = 0
            else:
                try:
                    print agent.epsilon, agent.name
                except:
                    pass
                agent.reset()
            i += 1

        for i in killers:
            self.agents[i-1].kills += 1

        for agent in self.agents:
            if agent.is_alive:
                agent.observe(observations[agent.name], min(1, max(-1, agent.reward)))

        bullets_to_drop = []
        for i in range(len(self.bullets)):
            self.bullets[i].update(self.obstacles, self.agents)
            if self.bullets[i].exploded:
                bullets_to_drop = [i] + bullets_to_drop
        for i in bullets_to_drop:
            self.bullets = self.bullets[:i] + self.bullets[i+1:]

        bonuses_to_drop = []
        for i in range(len(self.bonuses)):
            self.bonuses[i].update(self.agents)
            if self.bonuses[i].taken:
                bonuses_to_drop = [i] + bonuses_to_drop
        for i in bonuses_to_drop:
            self.bonuses = self.bonuses[:i] + self.bonuses[i+1:]

        self.fill_holder()

        frame_time = 1.0/FPS
        time_taken = time()-start
        if time_taken < frame_time:
            pass
            # sleep(frame_time-time_taken)
        else:
            pass
            # print 'too slow!', time_taken, 'instead of', frame_time
        if max(i.kills for i in self.agents) >= MAX_SCORE or self.ticks > self.episode_duration:
            save_result(self.stats, 'logs/'+str(self.round)+'.log')
            self.reset()
            self.round += 1
            print 'ROUND', self.round
            self.ticks = 0
            for i in self.agents:
                try:
                    print i.name, i.epsilon
                except:
                    pass
        # if self.round>1:
        #    1/0
