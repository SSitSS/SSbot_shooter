from base_agent import BaseAgent
import pygame
from keras.layers import Input, Dense, Flatten, Convolution1D, MaxPooling1D, BatchNormalization, AveragePooling1D
from keras.models import Model, load_model
from keras.optimizers import RMSprop
import numpy as np
from random import random, sample, randint
from math import tanh

actions_list = ['to_go_forward', 'to_go_back', 'to_go_left', 'to_go_right',
                'to_turn_left', 'to_turn_right', 'to_shoot', 'to_take_pistol',
                'to_take_shotgun', 'to_take_rocket_launcher', 'to_take_machine_gun']


def sample_from_memory(mem1, mem2, batch_size):
    if len(mem1) != len(mem2):
        raise ValueError('Memories must have same length to sample!')
    elif len(mem2) < batch_size:
        raise ValueError('Memories must be larger than batches!')
    indexes = range(len(mem1))
    while 1:
        #to_take = sample(indexes, batch_size)
        to_take = [randint(0, len(mem1)-1)]
        yield ([mem1[i] for i in to_take], [mem2[i] for i in to_take])


def get_random_actions(prev):
    actions = {}
    crit = 0.25

    fw_bw = int(prev['to_go_forward']) - int(prev['to_go_back']) + 2*random()-0.9
    if fw_bw > crit:
        actions['to_go_forward'] = True
        actions['to_go_back'] = False
    elif fw_bw < -crit:
        actions['to_go_forward'] = False
        actions['to_go_back'] = True
    else:
        actions['to_go_forward'] = False
        actions['to_go_back'] = False

    r_l = int(prev['to_go_right']) - int(prev['to_go_left']) + 2*random()-1
    if r_l > crit:
        actions['to_go_right'] = True
        actions['to_go_left'] = False
    elif r_l < -crit:
        actions['to_go_right'] = False
        actions['to_go_left'] = True
    else:
        actions['to_go_right'] = False
        actions['to_go_left'] = False

    r_l = int(prev['to_turn_right']) - int(prev['to_turn_left']) + 2*random()-1
    if r_l > crit:
        actions['to_turn_right'] = True
        actions['to_turn_left'] = False
    elif r_l < -crit:
        actions['to_turn_right'] = False
        actions['to_turn_left'] = True
    else:
        actions['to_turn_right'] = False
        actions['to_turn_left'] = False

    actions['to_shoot'] = random() > 0.9
    weapons = [False]*4
    weapons[randint(0, 3)] = True
    actions['to_take_pistol'], actions['to_take_shotgun'], actions['to_take_rocket_launcher'], actions['to_take_machine_gun'] = weapons
    return actions


class KeyboardAgent(BaseAgent):
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
        BaseAgent.__init__(self,
                           max_velocity,
                           turn_speed,
                           max_health,
                           max_armor,
                           spawn_point,
                           starting_angle,
                           starter_weapon_pack,
                           starter_ammo_pack,
                           color,
                           radius)

    def think(self, observation):
        #actions = {}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                self.actions['to_take_pistol'] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_1:
                self.actions['to_take_pistol'] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                self.actions['to_take_shotgun'] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_2:
                self.actions['to_take_shotgun'] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_3:
                self.actions['to_take_rocket_launcher'] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_3:
                self.actions['to_take_rocket_launcher'] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_4:
                self.actions['to_take_machine_gun'] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_4:
                self.actions['to_take_machine_gun'] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                self.actions['to_go_forward'] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_w:
                self.actions['to_go_forward'] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                self.actions['to_go_left'] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_a:
                self.actions['to_go_left'] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                self.actions['to_go_right'] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_d:
                self.actions['to_go_right'] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self.actions['to_go_back'] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_s:
                self.actions['to_go_back'] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self.actions['to_turn_left'] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_q:
                self.actions['to_turn_left'] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self.actions['to_turn_right'] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_e:
                self.actions['to_turn_right'] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.actions['to_shoot'] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.actions['to_shoot'] = False
        return self.actions

    def observe(self, observation, reward):
        pass


class EmptyAgent(BaseAgent):
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
        BaseAgent.__init__(self,
                           max_velocity,
                           turn_speed,
                           max_health,
                           max_armor,
                           spawn_point,
                           starting_angle,
                           starter_weapon_pack,
                           starter_ammo_pack,
                           color,
                           radius)


class RandomAgent(BaseAgent):
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
        BaseAgent.__init__(self,
                           max_velocity,
                           turn_speed,
                           max_health,
                           max_armor,
                           spawn_point,
                           starting_angle,
                           starter_weapon_pack,
                           starter_ammo_pack,
                           color,
                           radius)

    def think(self, observation):
        self.actions = get_random_actions(self.actions)


class PerceptronAgent(BaseAgent):
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
        BaseAgent.__init__(self,
                           max_velocity,
                           turn_speed,
                           max_health,
                           max_armor,
                           spawn_point,
                           starting_angle,
                           starter_weapon_pack,
                           starter_ammo_pack,
                           color,
                           radius)
        input_layer = Input(shape=(17, 13))
        flattened_input = Flatten()(input_layer)
        inner_layer = Dense(20, activation='relu')(flattened_input)
        output_layer = Dense(11, activation='tanh')(inner_layer)
        self.model = Model(input_layer, output_layer)
        self.model.compile(RMSprop(),
                           loss='hinge')
        self.delta = 1-1e-5
        self.epsilon = 1

    def think(self, observation):
        global actions_list
        observation = np.array(observation)
        try:
            r = random()
            if r < self.epsilon:
                actions = [random()**2 > 0.95 for i in range(11)]
            else:
                observation = observation.reshape((1, 17, 13))
                pred = self.model.predict(observation)
                actions = [i > 0 for i in pred[0]]
            self.actions = {actions_list[i]: actions[i] for i in range(11)}
            self.epsilon *= self.delta
        except:
            pass

    def observe(self, observation, reward):
        global actions_list
        observation = np.array(observation)
        try:
            observation = observation.reshape((1, 13, 17))
            actions = np.array([int(self.actions[i])*reward for i in actions_list])
            actions = actions.reshape((1, 11))
            self.model.fit(observation, actions, nb_epoch=1, verbose=0)
        except:
            pass


class BetterPerceptronAgent(BaseAgent):
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
        BaseAgent.__init__(self,
                           max_velocity,
                           turn_speed,
                           max_health,
                           max_armor,
                           spawn_point,
                           starting_angle,
                           starter_weapon_pack,
                           starter_ammo_pack,
                           color,
                           radius)
        input_layer = Input(shape=(17, 13))
        flattened_input = Flatten()(input_layer)
        inner_layer = Dense(20, activation='relu')(flattened_input)
        output_layer = Dense(11, activation='tanh')(inner_layer)
        self.model = Model(input_layer, output_layer)
        self.model.compile(RMSprop(),
                           loss='hinge')
        self.delta = 1-1e-5
        self.epsilon = 1

    def think(self, observation):
        global actions_list
        observation = np.array(observation)
        try:
            r = random()
            if r < self.epsilon:
                self.actions = get_random_actions(self.actions)
            else:
                observation = observation.reshape((1, 17, 13))
                pred = self.model.predict(observation)
                actions = [i > 0 for i in pred[0]]
                self.actions = {actions_list[i]: actions[i] for i in range(11)}
            self.epsilon *= self.delta
        except:
            pass

    def observe(self, observation, reward):
        global actions_list
        observation = np.array(observation)
        try:
            observation = observation.reshape((1, 13, 17))
            actions = np.array([int(self.actions[i])*reward for i in actions_list])
            actions = actions.reshape((1, 11))
            self.model.fit(observation, actions, nb_epoch=1, verbose=0)
        except:
            pass


class DQNAgent(BaseAgent):
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
        BaseAgent.__init__(self,
                           max_velocity,
                           turn_speed,
                           max_health,
                           max_armor,
                           spawn_point,
                           starting_angle,
                           starter_weapon_pack,
                           starter_ammo_pack,
                           color,
                           radius)
        #input_layer = Input(shape=(17, 13))
        #inner_layer1 = Convolution1D(20, 5, activation='relu')(input_layer)
        #pooling1 = MaxPooling1D(2)(inner_layer1)
        #inner_layer2 = Convolution1D(20, 3, activation='relu')(pooling1)
        #pooling2 = MaxPooling1D(2)(inner_layer2)
        #flattened = Flatten()(pooling2)
        #inner_layer3 = Dense(20, activation='relu')(flattened)
        #bn = BatchNormalization()(inner_layer3)
        #output_layer = Dense(11, activation='tanh')(bn)
        #self.model = Model(input_layer, output_layer)
        #self.model.compile(RMSprop(),
        #                   loss='hinge')

        self.delta = 1-1e-5 #decrease coefficient of epsilon-greedy
        self.epsilon = 1 #probability of random action

        self.max_memory_size = 50000
        self.observation_memory = []
        self.action_memory = []

        self.max_buffer_size = 100
        self.observation_buffer = []
        self.action_buffer = []
        self.reward_buffer = []

        self.tau = 0.97

        self.batch_size = 16

        self.skip = 5
        self.t = 0

        self.episode_rewards = []

        self.age = 0

        self.to_learn = True

    def set_model(self, config):
        layer_descriptions = config.split('\n')
        layers = [Input(shape=(17, 13))]
        prev_ind = 0
        for line in layer_descriptions:
            parameters = line.split('-')
            for i in range(len(parameters)):
                if parameters[i].isdigit():
                    parameters[i] = int(parameters[i])
            if parameters[0] == 'dense':
                layers.append(Dense(parameters[1], activation=parameters[2])(layers[prev_ind]))
            elif parameters[0] == 'conv':
                layers.append(Convolution1D(parameters[1], parameters[2], activation=parameters[3])(layers[prev_ind]))
            elif parameters[0] == 'flatten':
                layers.append(Flatten()(layers[prev_ind]))
            elif parameters[0] == 'bn':
                layers.append(BatchNormalization()(layers[prev_ind]))
            elif parameters[0] == 'mp':
                layers.append(MaxPooling1D(parameters[1])(layers[prev_ind]))
            elif parameters[0] == 'avp':
                layers.append(AveragePooling1D(parameters[1])(layers[prev_ind]))
            else:
                raise ValueError(parameters)
            prev_ind += 1
        layers.append(Dense(11, activation='tanh')(layers[-1]))
        self.model = Model(layers[0], layers[-1])
        self.model.compile(RMSprop(),
                           loss='hinge')

    def load(self, filename):
        self.model = load_model(filename)

    def reset(self):
        self.angle = self.spawn_angle
        self.hp = self.max_hp
        self.arm = 0
        self.x, self.y = self.spawn_point
        self.ammo = [10, 5, 1]
        self.is_alive = True
        self.killed_by = -1
        self.to_resurrect = -1
        self.age += 1
        self.observation_buffer = []
        self.action_buffer = []
        self.reward_buffer = []
        if self.to_learn:
            self.model.save('saved/' + self.name + str(self.age) + '.h5')
            with open('rewards_log/'+self.name+str(self.age)+'.log', 'w') as f:
                f.write(' '.join([str(i) for i in self.episode_rewards]))
        self.episode_rewards = []

    def bufferize(self, observation, reward, actions):
        self.observation_buffer.append(observation)
        self.reward_buffer.append(reward)
        self.action_buffer.append(actions)
        if len(self.observation_buffer) > self.max_buffer_size and \
           len(self.action_buffer) > self.max_buffer_size and \
           len(self.reward_buffer) > self.max_buffer_size:
            self.observation_buffer = self.observation_buffer[1:]
            self.action_buffer = self.action_buffer[1:]
            self.reward_buffer = self.reward_buffer[1:]

    def update_memory(self):
        max_reward = sum([self.tau**i for i in range(self.max_buffer_size)])
        if len(self.observation_buffer) == len(self.reward_buffer) == self.max_buffer_size:
            new_actions = self.action_buffer[0].copy()
            total_reward = sum([(self.tau**i)*self.reward_buffer[i] for i in range(self.max_buffer_size)])
            self.episode_rewards.append(tanh(total_reward)/tanh(max_reward))
            if total_reward != 0:
                for j in range(self.action_buffer[0].shape[1]):
                    computed = total_reward*new_actions[0][j]
                    new_actions[0][j] = tanh(computed)/tanh(max_reward)
                self.action_memory.append(new_actions)
                self.observation_memory.append(self.observation_buffer[0])
                if len(self.action_memory) > self.max_memory_size and \
                   len(self.observation_memory) > self.max_memory_size:
                    self.observation_memory = self.observation_memory[-self.max_memory_size:]
                    self.action_memory = self.action_memory[-self.max_memory_size:]
        else:
            pass

    def think(self, observation):
        global actions_list
        observation = np.array(observation)
        try:
            r = random()
            if self.t == 0:
                if r < self.epsilon and self.to_learn:
                    #actions = [random()**2 > 0.95 for i in range(11)]
                    self.actions = get_random_actions(self.actions)
                else:
                    observation = observation.reshape((1, 17, 13))
                    pred = self.model.predict(observation)
                    actions = [i > 0.1 for i in pred[0]]
                    self.actions = {actions_list[i]: actions[i] for i in range(11)}
                self.epsilon *= self.delta
        except:
            pass

    def observe(self, observation, reward):
        global actions_list
        observation = np.array(observation)
        try:
            if self.to_learn:
                self.t = (self.t + 1) % self.skip
                observation = observation.reshape((1, 17, 13))
                actions = np.array([int(self.actions[i]) for i in actions_list])
                actions = actions.reshape((1, 11))

                self.bufferize(observation, reward, actions)
                self.update_memory()
                if self.batch_size < len(self.action_memory) and \
                   self.batch_size < len(self.observation_memory) and \
                   self.t == 0:
                    self.model.fit_generator(sample_from_memory(self.observation_memory, self.action_memory, self.batch_size),
                                             samples_per_epoch=self.batch_size, nb_epoch=1, verbose=0)
        except:
            print 'something went wrong'



