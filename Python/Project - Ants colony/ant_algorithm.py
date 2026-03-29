import pygame
import time
import random as rd
import numpy as np
from scipy.ndimage import gaussian_filter

def deg(rad): # rad -> deg
    return(180 * rad / np.pi)

def polygon_collision(poly1, poly2): # Separating Axis Theorem to test the collision between 2 convex polygons
    def get_axes(poly):
        axes = []
        for i in range(len(poly)):
            p1 = pygame.math.Vector2(poly[i])
            p2 = pygame.math.Vector2(poly[(i+1) % len(poly)])
            edge = p2 - p1
            normal = pygame.math.Vector2(-edge.y, edge.x).normalize()
            axes.append(normal)
        return axes

    def project(poly, axis):
        dots = [pygame.math.Vector2(p).dot(axis) for p in poly]
        return min(dots), max(dots)

    axes = get_axes(poly1) + get_axes(poly2)

    for axis in axes:
        min1, max1 = project(poly1, axis)
        min2, max2 = project(poly2, axis)

        if max1 < min2 or max2 < min1:
            return False  # séparation trouvée

    return True

class Ant:
    def __init__(self, x, y):
        self.rng = np.random.default_rng()
        self.x = x
        self.y = y
        self.th = 2 * np.pi * rd.random()
        self.speed = 100
        self.original_image = pygame.image.load('ant.png')
        self.image = self.original_image # image vers le haut au départ
        self.rect = self.image.get_rect(center = (x,y))
        self.cone_length = 100
        self.cone_width = 120
        self.cone = [0,-1,1] # very small initialization cone
        self.interaction_length = 10
        self.food_lock = False
        self.food_locked = Food(0,0)
        self.has_food = False
        self.nest_lock = False
        self.nest = Nest(0,0)
        self.choice_length = 50
        self.choice_width = 50
        self.left_captor_pos = [0,0]
        self.right_captor_pos = [0,0]
    
    def update_captor_position(self):
        pos = pygame.math.Vector2(self.x, self.y)
        direction = pygame.math.Vector2(np.cos(self.th), -np.sin(self.th))
        perp = pygame.math.Vector2(-direction.y, direction.x)
        tip = pos + direction * self.choice_length
        self.left_captor_pos = tip - perp * (self.choice_width/2)
        self.right_captor_pos = tip + perp * (self.choice_width/2)
    
    def move(self, dt, cR, cL, obstacles):

        b = False
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                vx = np.cos(self.th)
                vy = np.sin(self.th)
                if self.x < obstacle.rect.left or self.x > obstacle.rect.right:
                    vx = -vx
                if self.y < obstacle.rect.top or self.y > obstacle.rect.bottom:
                    vy = -vy
                th = np.atan2(vy, vx)
                b = True
                break
            
        if not b: # if no collision

            if self.food_lock: # if food is seen while no food on them
                dirx = self.food_locked.x - self.x
                diry = - (self.food_locked.y - self.y)
                th_target = np.arctan2(diry, dirx)
                dth = (th_target - self.th) % 2*np.pi
                if dth > np.pi:
                    dth = dth - 2*np.pi # dth between -pi and +pi
                max_turn = 3.0 * dt   # vitesse angulaire max
                dth = max(-max_turn, min(max_turn, dth))
                th = self.th + dth
            
            elif self.nest_lock: # if nest is seen with food on them
                dirx = self.nest.x - self.x
                diry = - (self.nest.y - self.y)
                th_target = np.arctan2(diry, dirx)
                dth = (th_target - self.th) % 2*np.pi
                if dth > np.pi:
                    dth -= 2*np.pi # dth between -pi and +pi
                max_turn = 3.0 * dt   # vitesse angulaire max
                dth = max(-max_turn, min(max_turn, dth))
                th = self.th + dth

            else:
                k = 1
                alpha = 2
                bias = ( (k + cL)**alpha - (k + cR)**alpha )
                dth_max = 0.3  # angle max par step
                th_avg = self.th + dth_max * bias / ( (k + cL)**alpha + (k + cR)**alpha )
                th = self.rng.normal(th_avg, np.pi/50)

        self.th = th
        A = 1
        if b:
            A = 5
        c = np.cos(self.th)
        s = np.sin(self.th)
        self.x += c * self.speed * dt * A
        self.y -= s * self.speed * dt * A
        self.rect.center = (self.x, self.y) # modification du centre de la position

    def draw(self, screen):
        # rotation sprite
        self.image = pygame.transform.rotate(self.original_image, deg(self.th - np.pi/2))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, self.rect)

        # cone
        pos = pygame.math.Vector2(self.x, self.y)
        direction = pygame.math.Vector2(np.cos(self.th), -np.sin(self.th))
        perp = pygame.math.Vector2(-direction.y, direction.x)
        tip = pos + direction * self.cone_length
        left = tip + perp * (self.cone_width/2)
        right = tip - perp * (self.cone_width/2)
        self.cone = [pos, left, right]
        """
        pygame.draw.polygon(screen, (200, 200, 200), self.cone, 2) # DRAW CONES
        """

class Obstacle:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x,y,w,h)
        self.color = (150,150,150)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        image = pygame.image.load('ball_rouge.png')
        scale = 0.6
        w = image.get_width()
        h = image.get_height()
        self.image = pygame.transform.scale(image, (int(w*scale), int(h*scale)))
        self.rect = self.image.get_rect(center = (x,y))
        self.rect_points = [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft]
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Nest:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        image = pygame.image.load('blue_ball.png')
        scale = 0.4
        w = image.get_width()
        h = image.get_height()
        self.image = pygame.transform.scale(image, (int(w*scale), int(h*scale)))
        self.rect = self.image.get_rect(center = (x,y))
        self.rect_points = [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft]
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Game:

    def __init__(self,screen, Nx, Ny):
        N_ant = 150
        N_food = 20
        self.screen = screen
        self.running = True # fenêtre ouverte ou non
        self.clock = pygame.time.Clock() # horloge
        self.init_time = time.time()
        self.nest = Nest(int(Nx/2), int(Ny/2))
        self.ants = [Ant(int(Nx/2),int(Ny/2)) for _ in range(N_ant)]
        foods1 = [Food(int(rd.random()*100 + int(3*Nx/4)), int(rd.random()*100 + int(3*Ny/4))) for _ in range(int(N_food/2))]
        foods2 = [Food(int(rd.random()*100 + int(Nx/4)), int(rd.random()*100 + int(3*Ny/4))) for _ in range(int(N_food/2))]
        self.foods = foods1 + foods2
        self.obstacles = [Obstacle(int(Nx/2), int(5*Ny/8), 200, 300), Obstacle(int(Nx/6), int(Ny/6), 400, 200),
                          Obstacle(0,0,10,Ny), Obstacle(0,0,Nx,10), Obstacle(0,Ny-10,Nx,10), Obstacle(Nx-10,0,10,Ny)]
        self.evaporation_rate = 0.1
        self.dx = 10
        self.dy = 10
        self.Nx = Nx
        self.Ny = Ny
        self.nx = int(Nx/self.dx)
        self.ny = int(Ny/self.dy)
        self.grid_food = np.zeros((self.nx, self.ny))
        self.grid_nest = np.zeros((self.nx, self.ny))
        self.D = 1

    def handling_events(self):
        for event in pygame.event.get(): # liste des événements en cours : pour fermer la fenêtre eg
                if event.type == pygame.QUIT:
                    self.running = False

    def update(self, dt):
        for ant in self.ants:
            # if ant has no food
            cR = 0
            cL = 0 # no initial gradient
            if not ant.has_food:
                # if ant hasn't seen food
                if not ant.food_lock:
                    for food in self.foods: # looks if there is food in front and locks its trajectory if yes
                        if polygon_collision(ant.cone, food.rect_points):
                            ant.food_lock = True
                            ant.food_locked = food
                            break
                # if the ant sees food
                else:
                    if ant.food_locked in self.foods: # if food still available
                        if (ant.food_locked.x - ant.x)**2 + (ant.food_locked.y - ant.y)**2 <= ant.interaction_length**2:
                            ant.has_food = True
                            """
                            self.foods.remove(ant.food_locked) # FINITE RESOURCES
                            """
                            ant.food_lock = False
                    else: # not available : change target
                        ant.food_lock = False
                # droped food search pheromones
                i = int(ant.x / self.dx)
                j = int(ant.y / self.dy)
                self.grid_nest[i, j] += 1
                # looking for food search pheromones
                k = int(ant.right_captor_pos[0]/self.dx) % self.nx
                l = int(ant.right_captor_pos[1]/self.dy) % self.ny
                m = int(ant.left_captor_pos[0]/self.dx) % self.nx
                n = int(ant.left_captor_pos[1]/self.dy) % self.ny
                cR = self.grid_food[k, l]
                cL = self.grid_food[m, n]
            # if ant has food
            else:
                ant.food_lock = False
                # if ant hasn't seen nest
                if not ant.nest_lock:
                    if polygon_collision(ant.cone, self.nest.rect_points):
                        ant.nest_lock = True
                        ant.nest = self.nest
                # if the ant sees the nest
                else:
                    if (self.nest.x - ant.x)**2 + (self.nest.y - ant.y)**2 <= ant.interaction_length**2 :
                        ant.has_food = False
                        ant.nest_lock = False
                # nest search pheromones
                i = int(ant.x / self.dx)
                j = int(ant.y / self.dy)
                self.grid_food[i, j] += 1
                # looking for nest search pheromones
                k = int(ant.right_captor_pos[0]/self.dx) % self.nx
                l = int(ant.right_captor_pos[1]/self.dy) % self.ny
                m = int(ant.left_captor_pos[0]/self.dx) % self.nx
                n = int(ant.left_captor_pos[1]/self.dy) % self.ny
                cR = self.grid_nest[k, l]
                cL = self.grid_nest[m, n]
            ant.update_captor_position()
            ant.move(dt, cR, cL, self.obstacles)
            ant.x %= Nx
            ant.y %= Ny
        lap_food = (
            np.roll(self.grid_food, 1, axis=0) +
            np.roll(self.grid_food, -1, axis=0) +
            np.roll(self.grid_food, 1, axis=1) +
            np.roll(self.grid_food, -1, axis=1) -
            4*self.grid_food
        )
        self.grid_food = self.grid_food + self.D * dt * lap_food - self.evaporation_rate * self.grid_food * dt
        lap_nest = (
            np.roll(self.grid_nest, 1, axis=0) +
            np.roll(self.grid_nest, -1, axis=0) +
            np.roll(self.grid_nest, 1, axis=1) +
            np.roll(self.grid_nest, -1, axis=1) -
            4*self.grid_nest
        )
        self.grid_nest = self.grid_nest + self.D * dt * lap_nest - self.evaporation_rate * self.grid_nest * dt
    
    def display(self):
        self.screen.fill('white')

        smooth_grid_food = gaussian_filter(self.grid_food, sigma=1)
        smooth_grid_nest = gaussian_filter(self.grid_nest, sigma=1)

        size_x = smooth_grid_food.shape[0]
        size_y = smooth_grid_food.shape[1]

        # --- Heatmaps des phéromones ---
        surface_food = pygame.Surface((size_x, size_y), pygame.SRCALPHA)
        surface_nest = pygame.Surface((size_x, size_y), pygame.SRCALPHA)

        # Normalisation pour couleur
        if smooth_grid_food.max() > 0:
            food_norm = (smooth_grid_food / smooth_grid_food.max() * 255).astype(np.uint8)
        else:
            food_norm = smooth_grid_food.astype(np.uint8)

        if smooth_grid_nest.max() > 0:
            nest_norm = (smooth_grid_nest / smooth_grid_nest.max() * 255).astype(np.uint8)
        else:
            nest_norm = smooth_grid_nest.astype(np.uint8)

        # créer surface RGB
        rgb = np.ones((food_norm.shape[0], food_norm.shape[1], 3), dtype=np.uint8) * 255
        rgb[:,:,2] = 255 - food_norm   # rouge
        rgb[:,:,0] = 255 - nest_norm   # bleu

        surface = pygame.surfarray.make_surface(rgb)

        # si besoin ajuster à l'écran
        surface = pygame.transform.smoothscale(surface, (self.Nx, self.Ny))

        self.screen.blit(surface, (0,0))

        self.screen.blit(surface_food, (0,0))
        self.screen.blit(surface_nest, (0,0))

        # Dessin classique
        for food in self.foods:
            food.draw(self.screen)
        self.nest.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        for ant in self.ants:
            ant.draw(self.screen)

        pygame.display.flip()
    
    def run(self):
        while self.running:
            dt = self.clock.tick(120) / 1000
            self.handling_events()
            self.update(dt)
            self.display()

pygame.init()

Nx = 1550
Ny = 870
screen = pygame.display.set_mode((Nx,Ny)) # taille de la fenêtre ouverte. (0,0) : plein écran
game = Game(screen, Nx, Ny)
game.run()

pygame.quit()