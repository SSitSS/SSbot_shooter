map_size = [1080, 720]

# walls color
clr = '#888888'

# walls and columns positions
map_walls = []
map_walls.append(((540, 170), 1080, 20, clr))
map_walls.append(((540, 550), 1080, 20, clr))
map_walls.append(((910, 360), 20, 720, clr))
map_walls.append(((170, 360), 20, 720, clr))

map_columns = [((150, 150), 30, clr),
               ((930, 150), 30, clr),
               ((930, 570), 30, clr),
               ((150, 570), 30, clr)]
               #((200, 200), 20, clr),
               #((880, 200), 20, clr),
               #((880, 520), 20, clr),
               #((200, 520), 20, clr)]


default_parameters = {'max_velocity': 1.2,
                      'turn_speed': 0.05,
                      'max_health': 100,
                      'max_armor': 100,
                      'spawn_point': (300, 200),
                      'starting_angle': 0,
                      'starter_weapon_pack': None,
                      'starter_ammo_pack': None,
                      'color': '#4444dd',
                      'radius': 12}

# Agents generating (without decision functions)
map_agents = [('DQNAgent', default_parameters.copy())]




# Bonuses spawn points with timeouts
map_bonuses = [[(300, 200, 250), (300, 335, 250), (300, 470, 250), (540, 200, 250), (540, 470, 250), (780, 200, 250), (780, 335, 250), (780, 470, 250)],  # bullet packs
               [(350, 250, 250), (350, 420, 250), (730, 250, 250), (730, 420, 250)],  # shells packs
               [(350, 335, 250), (730, 335, 250)],  # rockets packs
               [(540, 250, 250)],  # medkits
               [(540, 420, 250)]]  # armor vests
