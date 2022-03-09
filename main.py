import pygame
import numpy as np
import math

pygame.init()
WIDTH, HEIGHT = 500, 700
WHITE = (255, 255, 255)
FPS = 60
MAX_D = np.linalg.norm(np.array([WIDTH, HEIGHT]) - np.array([0, 0]))
walls_num = 8


class Boundary:
    def __init__(self, x1, y1, x2, y2):
        self.start = np.array([x1, y1])
        self.end = np.array([x2, y2])

    def render(self, win):
        pygame.draw.line(win, WHITE, self.start, self.end)


class Ray:
    def __init__(self, pos, angle, num):
        self.pos = np.array([pos[0], pos[1]])
        self.angle = angle
        radianAngle = math.radians(angle)
        dx = math.sin(radianAngle) * 1
        dy = -math.cos(radianAngle) * 1
        self.direction = np.array([dx, dy])
        self.magnitude = 10
        self.number = num

    def look_at(self, pos):
        vector = np.array([pos[0] - self.pos[0], pos[1] - self.pos[1]])
        self.direction = vector / np.linalg.norm(vector)

    def cast(self, wall):
        x1 = wall.start[0]
        y1 = wall.start[1]
        x2 = wall.end[0]
        y2 = wall.end[1]
        x3 = self.pos[0]
        y3 = self.pos[1]
        end = self.pos + self.direction
        x4 = end[0]
        y4 = end[1]
        down = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if down == 0:
            return None
        topT = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
        t = topT / down
        topU = (x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)
        u = -topU / down
        if (0 < t < 1) and u > 0:
            x0 = x1 + t * (x2 - x1)
            y0 = y1 + t * (y2 - y1)
            return np.array([x0, y0])
        return None

    def render(self, win):
        end = self.pos + (self.direction * self.magnitude)
        pygame.draw.line(win, WHITE, self.pos,
                         end)


class Camera:
    def __init__(self, scene_range=45):
        self.offset = 90
        self.pos = np.array([WIDTH / 2, HEIGHT / 2])
        self.rays = []
        self.range = scene_range
        self.create_rays()

    def create_rays(self):
        for i in np.arange(0, self.range, .3):
            self.rays.append(Ray(self.pos, i + self.offset, i))

    def cast(self, win, walls):
        scenes = []
        for ray in self.rays:
            min_dis = MAX_D
            min_pt = None
            min_wall = -1
            for wall in walls:
                pt = ray.cast(wall)
                if pt is not None:
                    dis = np.linalg.norm(pt - self.pos)
                    dis *= math.cos(math.radians(ray.number))
                    if dis < min_dis:
                        min_pt = pt
                        min_dis = dis
                        min_wall = walls.index(wall)
            if min_pt is not None:
                pygame.draw.circle(win, (0, 0, 255), min_pt, 3)
                pygame.draw.line(win, WHITE, self.pos, min_pt)
            scenes.append((min_dis, min_wall))
        return scenes

    def render(self, win):
        pygame.draw.circle(win, WHITE, self.pos, 2)
        for ray in self.rays:
            ray.render(win)

    def update(self, pos):
        self.pos = np.array([pos[0], pos[1]])
        self.rays = []
        self.create_rays()

    def add_offset(self, offset):
        self.offset += offset
        self.rays = []
        self.create_rays()


def create_walls(amount):
    walls = []
    x1s = np.random.randint(0, WIDTH, amount)
    x2s = np.random.randint(0, WIDTH, amount)
    y1s = np.random.randint(0, HEIGHT, amount)
    y2s = np.random.randint(0, HEIGHT, amount)
    for x1, y1, x2, y2 in zip(x1s, y1s, x2s, y2s):
        walls.append(Boundary(x1, y1, x2, y2))
    walls.append(Boundary(0, 0, WIDTH, 0))
    walls.append(Boundary(0, 0, 0, HEIGHT))
    walls.append(Boundary(WIDTH, 0, WIDTH, HEIGHT))
    walls.append(Boundary(0, HEIGHT, WIDTH, HEIGHT))
    return walls


def normalize(value, min_v, max_v, min_nv, max_nv):
    return ((value - min_v) / (max_v - min_v)) * (max_nv - min_nv) + min_nv


def main():
    win = pygame.display.set_mode((WIDTH * 2, HEIGHT))
    pygame.display.set_caption("Raycasting")
    clock = pygame.time.Clock()
    run = True
    walls = create_walls(walls_num)
    camera = Camera(scene_range = 40)
    offset_angle = 1
    colors = []
    for _ in walls:
        colors.append((np.random.randint(0, 100), np.random.randint(0, 100), np.random.randint(0, 100)))
    colors.append((0, 0, 0))
    colors = np.array(colors)
    while run:
        clock.tick(FPS)
        pygame.draw.rect(win, (0, 0, 0), (0, 0, WIDTH * 2, HEIGHT))
        camera.update(pygame.mouse.get_pos())
        scenes = camera.cast(win, walls)
        camera.render(win)
        for wall in walls:
            wall.render(win)
        scene_width = WIDTH / len(scenes)
        center = HEIGHT / 2
        for i in range(len(scenes)):
            dis = scenes[i][0]
            wall = scenes[i][1]
            brightness = normalize(dis ** 2, 0, MAX_D ** 2, 105, 0)
            height_r = normalize(dis ** 2, 0, MAX_D ** 2, HEIGHT / 2, 0)
            color = colors[wall] + brightness
            pygame.draw.rect(win, color,
                             (WIDTH + scene_width * i, center - height_r / 2, scene_width, height_r), 0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            camera.add_offset(-offset_angle)
        if keys[pygame.K_d]:
            camera.add_offset(offset_angle)
        pygame.display.update()


if __name__ == "__main__":
    main()
