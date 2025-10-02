import pygame
import random as rd

BACKGROUND = (100,100,100)

def f(u1,u2,mu):
    return mu*(1-u1**2)*u2-u1

def rk4(u1,u2,dt,mu):
    k1 = f(u1,u2,mu)
    k2 = f(u1+u2*dt/2,u2+k1*dt/2,mu)
    k3 = f(u1+dt/2*u2+dt**2/4*k1,u2+dt/2*k2,mu)
    k4 = f(u1+dt*u2+dt**2/2*k2,u2+dt*k3,mu)
    return (u1+dt*u2+dt**2/6*(k1+k2+k3),u2+dt/6*(k1+2*k2+2*k3+k4))

def draw_texte (texte, font, couleur, x, y, screen):
    image = font.render(texte, True, couleur)
    screen.blit(image, (x,y))


class Point:

    def __init__(self, u1, u2):
        self.image = pygame.image.load('point.png')
        self.x = 960+u1*100
        self.y = 540+u2*100
        self.rect = self.image.get_rect(x=self.x,y=self.y)

    def move(self):
        self.rect.center = (1920-self.x, self.y) # modification du centre de la position

    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    def divergence(self):
        if abs(self.x) > 1000000000 or abs(self.y) > 1000000000:
            self.x=0
            self.y=0


class Surface:

    def __init__(self, trail_fade):
        self.trail_surface = pygame.Surface((1920, 1080), pygame.SRCALPHA) # surface de traînée
        self.trail_fade = trail_fade # valeur pour le fondu (atténuation de la traînée : 0 à 255)

    def draw(self, screen):
        screen.blit(self.trail_surface, (0,0))


class Button:

    def __init__(self, up_down):
        self.up_down = up_down
        if up_down == 'up':
            self.image = pygame.image.load('up.png')
            self.x = 1550
            self.y = 400
        if up_down == 'down':
            self.image = pygame.image.load('down.png')
            self.x = 1550
            self.y = 580
        self.rect = self.image.get_rect(x=self.x, y=self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Game:

    def __init__(self, screen, n, mu): # x1, x2 valeurs initiales
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()
        self.ens_point = [Point(2-4*rd.random(),2-4*rd.random()) for k in range(n)]
        self.n = n
        self.trail_surface = Surface(250)
        self.up = Button('up')
        self.down = Button('down')
        self.t_up = 0
        self.t_down = 0
        self.mu = mu

    def handling_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        pos = pygame.mouse.get_pos()
        if self.up.rect.collidepoint(pos):
            
            if pygame.mouse.get_pressed()[0] == 1 and (pygame.time.get_ticks() - self.t_up) >= 5:
                self.t_up = pygame.time.get_ticks()
                self.mu += 0.01
        
        if self.down.rect.collidepoint(pos):

            if pygame.mouse.get_pressed()[0] == 1 and (pygame.time.get_ticks() - self.t_down) >= 5:
                self.t_down = pygame.time.get_ticks()
                self.mu -= 0.01
    
    def update(self,dt):
        for k in range(self.n):
            u1 = (self.ens_point[k].x-960)/100
            u2 = (self.ens_point[k].y-540)/100
            (u1_new,u2_new) = rk4(u1,u2,dt,self.mu)
            self.ens_point[k].x = 960+u1_new*100
            self.ens_point[k].y = 540+u2_new*100
            self.ens_point[k].divergence()
            self.ens_point[k].move()

    def display(self):
        self.trail_surface.trail_surface.fill((255, 255, 255, self.trail_surface.trail_fade), special_flags=pygame.BLEND_RGBA_MULT)
        screen.fill(BACKGROUND)
        self.trail_surface.draw(self.screen)
        for k in range(self.n):
            pygame.draw.circle(self.trail_surface.trail_surface, (0,0,0,255), (1920-self.ens_point[k].x, self.ens_point[k].y), 1)
            self.ens_point[k].draw(self.screen)
        self.up.draw(self.screen)
        self.down.draw(self.screen)
        draw_texte('µ = ' + str(round(self.mu,2)), pygame.font.SysFont('Arial', 50), (255,255,255), 1525, 250, self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(120) / 1000
            self.handling_events()
            self.update(dt)
            self.display()

pygame.init()

mu = 2

n = 1000

screen = pygame.display.set_mode((1920,1080))

game = Game(screen, n, mu)

game.run()

pygame.quit()