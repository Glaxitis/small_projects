import pygame
import numpy as np

WIDTH, HEIGHT = 1300, 800
CELL_SIZE = 10
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE

WHITE = (255, 255, 255)
BLACK = (0,0,0)


def draw_grid(grid):
    for row in range(ROWS):
        for col in range(COLS):
            color = BLACK if grid[row,col]==1 else WHITE
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def update_grid(grid):
    new_grid = grid.copy()
    for row in range(ROWS):
        for col in range(COLS):
            neighbors = np.sum(grid[row-1:row+2,col-1:col+2]) - grid[row,col]
            if grid[row,col] == 0 and neighbors == 3:
                new_grid[row,col] = 1
            elif grid[row,col] == 1 and (neighbors == 2 or neighbors == 3):
                new_grid[row,col] = 1
            else:
                new_grid[row,col] = 0
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
        self.clock.tick()

    def run(self):
        while self.running:
            self.handling_events()
            self.update()
            self.display()

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))

grid = np.random.choice([0,1], size=(ROWS, COLS), p=[0.9,0.1])

game = Game(screen, grid)

game.run()

pygame.quit()