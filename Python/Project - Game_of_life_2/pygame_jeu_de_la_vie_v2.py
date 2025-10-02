import pygame
import numpy as np

WIDTH, HEIGHT = 1300, 800
CELL_SIZE = 5
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE

n = 14
WHITE = (255, 255, 255)
RED = [(255//n * k,0,0) for k in range(n)]


def draw_grid(grid):
    for row in range(ROWS):
        for col in range(COLS):
            color = RED[grid[row,col]]
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def update_grid(grid):
    new_grid = grid.copy()
    for row in range(ROWS):
        for col in range(COLS):
            neighbors = [grid[row-1,col],grid[(row+1)%ROWS,col],grid[row,col-1],grid[row,(col+1)%COLS]]
            if (grid[row,col]+1) % n in neighbors:
                new_grid[row,col] = (grid[row,col] + 1) % n
    return new_grid

class Game:

    def __init__(self, screen, grid):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()
        self.grid = grid

    def handling_events(self):
        for event in pygame.event.get(): # liste des événements en cours : pour fermer la fenêtre eg
            if event.type == pygame.QUIT:
                self.running = False
    
    def update(self):
        self.grid = update_grid(self.grid)

    def display(self):
        screen.fill(WHITE)
        draw_grid(self.grid)
        pygame.display.flip()
        self.clock.tick(100)

    def run(self):
        while self.running:
            self.handling_events()
            self.update()
            self.display()

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))

grid = np.random.choice([k for k in range(n)], size=(ROWS, COLS), p=[1/n for k in range(n)])

game = Game(screen, grid)

game.run()

pygame.quit()