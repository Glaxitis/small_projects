#include <SFML/Graphics.hpp>
#include <random>
#include <iostream>

unsigned int WIDTH = 1300; unsigned int HEIGHT = 800;
int CELL_SIZE = 10;
int ROWS = HEIGHT/CELL_SIZE; int COLS = WIDTH/CELL_SIZE;

sf::RenderWindow window(sf::VideoMode({WIDTH, HEIGHT}), "Game of Life");

void update_grid(int** grid, int** grid2)
{
    for (int row=0; row<ROWS; ++row)
    {
        for (int col=0; col<COLS; ++col)
        {
            int neighbors = 0;
            for (int i = -1; i <= 1; ++i) 
            {
                for (int j = -1; j <= 1; ++j) 
                {
                    if (i == 0 && j == 0) continue;
                    
                    int ni = row + i;
                    int nj = col + j;
                    
                    if (ni >= 0 && ni < ROWS && nj >= 0 && nj < COLS) 
                    {
                        neighbors += grid[ni][nj];
                    }
                }
            }
            if (grid[row][col] == 0 && neighbors == 3)
            {
                grid2[row][col] = 1;
            }
            else if (grid[row][col] == 1 && (neighbors == 2 or neighbors == 3))
            {
                grid2[row][col] = 1;
            }
            else
            {
                grid2[row][col] = 0;
            }
        }
    }

    for (int i = 0; i < ROWS; ++i) {
        for (int j = 0; j < COLS; ++j) {
            grid[i][j] = grid2[i][j];
            grid2[i][j] = 0;
        }
    }

}

void draw_grid(int** grid)
{
    for (int row=0; row<ROWS; ++row)
    {
        for (int col=0; col<COLS; ++col)
        {
            sf::Color color;
            if (grid[row][col] == 1)
            {
                color = sf::Color::Black;
            }
            else
            {
                color = sf::Color::White;
            }
            sf::RectangleShape rect({float(CELL_SIZE), float(CELL_SIZE)});
            rect.setFillColor(color);
            rect.setPosition({float(col * CELL_SIZE), float(row * CELL_SIZE)});
            window.draw(rect);
        }
    }
}

int main()
{
    const int TARGET_FPS = 60;
    const sf::Time timePerFrame = sf::seconds(1.0f / TARGET_FPS);
    sf::Clock clock;
    sf::Time timeSinceLastUpdate = sf::Time::Zero;

    int** grid2 = new int*[ROWS];
    for (int i = 0; i < ROWS; ++i) {
        grid2[i] = new int[COLS];
    }

    for (int i = 0; i < ROWS; ++i) {
        for (int j = 0; j < COLS; ++j) {
            grid2[i][j] = 0;
        }
    }

    int** grid = new int*[ROWS];
    for (int i = 0; i < ROWS; ++i) {
        grid[i] = new int[COLS];
    }

    std::random_device rd;
    std::mt19937 gen(rd());
    std::bernoulli_distribution dis(0.1);

    for (int i = 0; i < ROWS; ++i) {
        for (int j = 0; j < COLS; ++j) {
            grid[i][j] = dis(gen) ? 1 : 0;
        }
    }

    for (int i = 0; i < ROWS; ++i) {
        for (int j = 0; j < COLS; ++j) {
            std::cout << grid[i][j];
        }
        std::cout << std::endl;
    }

    while (window.isOpen())
    {
        while (const std::optional event = window.pollEvent())
        {
            if (event -> is <sf::Event::Closed>())
                window.close();
        }

        sf::Time deltaTime = clock.restart();
        timeSinceLastUpdate += deltaTime;

        while (timeSinceLastUpdate >= timePerFrame)
        {
            timeSinceLastUpdate -= timePerFrame;
            
            window.clear();
            draw_grid(grid);
            window.display();
            update_grid(grid, grid2);
            
        }

        sf::sleep(timePerFrame - deltaTime);

    }

    for (int i = 0; i < ROWS; ++i) delete[] grid[i];
    delete[] grid;
    for (int i = 0; i < ROWS; ++i) delete[] grid2[i];
    delete[] grid2;

    return 0;

}