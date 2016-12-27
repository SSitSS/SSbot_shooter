import pygame


def line_point_distance(x1, y1, x2, y2, x0, y0):
    alpha = - ((x2-x1)*(x1-x0) + (y2-y1)*(y1-y0)) / ((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))
    if alpha < 0:
        xa, ya = x1, y1
    elif alpha > 1:
        xa, ya = x2, y2
    else:
        xa, ya = x1 + alpha*(x2-x1), y1 + alpha*(y2-y1)
    dist = ((x0-xa)**2+(y0-ya)**2)**0.5
    return dist


class Column:
    def __init__(self, center_pos, radius=25, color='#303030'):
        self.radius = radius
        self.x, self.y = center_pos
        self.color = pygame.Color(color)

    def draw(self, screen):
        pygame.draw.circle(screen,
                           self.color,
                           (self.x, self.y),
                           self.radius)

    def distance_to_point(self, x, y):
        return ((self.x-x)**2 + (self.y-y)**2)**0.5 - self.radius


class Wall:
    def __init__(self, center_pos, width=50, height=50, color='#303030'):
        self.width = width
        self.height = height
        self.x, self.y = center_pos
        self.rect = pygame.Rect(self.x-width/2, self.y-height/2,
                                width, height)
        self.color = pygame.Color(color)

    def draw(self, screen):
        pygame.draw.rect(screen,
                         self.color,
                         self.rect)

    def get_corners(self):
        return [(self.x-self.width/2, self.y-self.height/2),
                (self.x+self.width/2, self.y-self.height/2),
                (self.x+self.width/2, self.y+self.height/2),
                (self.x-self.width/2, self.y+self.height/2)]

    def get_sides(self):
        corners = self.get_corners()
        return [corners[0:2], corners[1:3], corners[2:4], [corners[0], corners[-1]]]

    def distance_to_point(self, x, y):
        sides = self.get_sides()
        return min([line_point_distance(i[0][0], i[0][1], i[1][0], i[1][1], x, y) for i in sides])
