#define _USE_MATH_DEFINES
#include <iostream>
#include <math.h>
#include <SFML/Graphics.hpp>
#include <random>

unsigned int WIDTH = 1500; unsigned int HEIGHT = 900;
int CELL_SIZE = 5;
int ROWS = HEIGHT/CELL_SIZE; int COLS = WIDTH/CELL_SIZE;

std::random_device rd;
std::mt19937 gen(rd());
std::uniform_real_distribution<> dis(-1.0, 1.0);

sf::RenderWindow window(sf::VideoMode({WIDTH, HEIGHT}), "Reaction - Diffusion");

void inv_transf(double& x, double& y, double x_min, double x_max, double y_min, double y_max) // transforme la coordonnée d'un pixel en la coordonnée absolue
{
    x = x_min + (x_max - x_min) * x / double(WIDTH);
    y = y_min + (y_max - y_min) * (double(HEIGHT) - y) / double(HEIGHT);
}

double initial_u(double x, double y)
{
    double sigma = 0.1;
    double deterministic_part = std::exp(- (x*x + y*y) / (2*sigma*sigma));
    double amplitude = 0.5;
    double noise = amplitude * dis(gen);
    double value = noise + deterministic_part;
    return std::max(-1.0, std::min(1.0, value));
}

double R(double u)
{
    return u * (1-u*u);
}

double laplacian(double u_x_pdr, double u_x_ndr, double u_y_pdr, double u_y_ndr, double u_xy, double dx, double dy)
{
    double sum1 = u_x_pdr + u_x_ndr - 2 * u_xy;
    double sum2 = u_y_pdr + u_y_ndr - 2 * u_xy;
    sum1 /= (dx * dx);
    sum2 /= (dy * dy);
    double result = sum1 + sum2;
    return result;
}

void update(double& u, double u_x_pdr, double u_x_ndr, double u_y_pdr, double u_y_ndr, double u_xy, double dt, double dx, double dy, double D) // t-dt -> t+dt
{
    u += dt * ( D * laplacian(u_x_pdr, u_x_ndr, u_y_pdr, u_y_ndr, u_xy, dx, dy) + R(u));
}

double** set_grid(double x_min = -1, double x_max = 1, double y_min = -1, double y_max = 1)
{
    double** grid = new double*[ROWS];
    for (int row = 0 ; row < ROWS ; ++row)
    {
        grid[row] = new double[COLS];
    }
    for (int row = 0 ; row < ROWS ; ++row)
    {
        for (int col = 0 ; col < COLS ; ++col)
        {
            double x = row * CELL_SIZE;
            double y = col * CELL_SIZE;
            inv_transf(x, y, x_min, x_max, y_min, y_max);
            grid[row][col] = initial_u(x, y);
        }
    }
    return grid;
}

double** set_grid2()
{
    double** grid = new double*[ROWS];
    for (int row = 0 ; row < ROWS ; ++row)
    {
        grid[row] = new double[COLS];
    }
    for (int row = 0 ; row < ROWS ; ++row)
    {
        for (int col = 0 ; col < COLS ; ++col)
        {
            grid[row][col] = 0;
        }
    }
    return grid;
}

void delete_grid(double** grid)
{
    for (int row = 0 ; row < ROWS ; ++row)
    {
        delete[] grid[row];
    }
    delete[] grid;
}

void update_grid(double** grid, double** grid2, double dt, double dx, double dy, double D, double x_min = -1, double x_max = 1, double y_min = -1, double y_max = 1)
{
    for (int row=0; row<ROWS; ++row)
    {
        for (int col=0; col<COLS; ++col)
        {
            double u = grid[row][col];
            double u_x_pdr = 0;
            double u_x_ndr = 0;
            double u_y_pdr = 0;
            double u_y_ndr = 0;

            if (col+1 < COLS) {u_x_pdr = grid[row][col+1];}
            if (col-1 >= 0) {u_x_ndr = grid[row][col-1];}
            if (row+1 < ROWS) {u_y_pdr = grid[row+1][col];}
            if (row-1 >= 0) {u_y_ndr = grid[row-1][col];}

            update(u, u_x_pdr, u_x_ndr, u_y_pdr, u_y_ndr, u, dt, dx, dy, D);
            grid2[row][col] = u; // new u
        }
    }
    for (int row=0; row<ROWS; ++row)
    {
        for (int col=0; col<COLS; ++col)
        {
            grid[row][col] = grid2[row][col];
            grid2[row][col] = 0;
        }
    }
}

sf::Color color_shade(double u) // -1 <= u <= 1 
{
    int intensity = int((1-u) / 2 * 255);
    sf::Color color(intensity, intensity, intensity);
    return color;
}

void draw_grid(double** grid)
{
    for (int row=0; row<ROWS; ++row)
    {
        for (int col=0; col<COLS; ++col)
        {
            double u = grid[row][col];
            sf::Color shade = color_shade(u);
            sf::RectangleShape rect({float(CELL_SIZE), float(CELL_SIZE)});
            rect.setFillColor(shade);
            rect.setPosition({float(col * CELL_SIZE), float(row * CELL_SIZE)});
            window.draw(rect);
        }
    }
}

int main()
{

    // render quantities

    const int TARGET_FPS = 20;
    const sf::Time timePerFrame = sf::seconds(1.0f / TARGET_FPS);
    sf::Clock clock;
    sf::Time timeSinceLastUpdate = sf::Time::Zero;

    float phys_accumulator = sf::Time::Zero.asSeconds(); // accumulated physical time 

    double x_min = - 1;
    double x_max = 1;
    double y_min = - 1;
    double y_max = 1;

    double dx = CELL_SIZE;
    double dy = CELL_SIZE;
    inv_transf(dx, dy, x_min, x_max, y_min, y_max);
    const double phys_dx = dx;
    const double phys_dy = dy;
    const double D = 1.0;
    const double phys_dt = 0.01;

    double** grid = set_grid(x_min, x_max, y_min, y_max);
    double** grid2 = set_grid2();

    while (window.isOpen())
    {
        while (const std::optional event = window.pollEvent())
        {
            if (event -> is <sf::Event::Closed>())
                window.close();
        }

        sf::Time deltaTime = clock.restart();
        timeSinceLastUpdate += deltaTime;
        phys_accumulator += deltaTime.asSeconds();

        while (phys_accumulator >= phys_dt) // physics part
        {

            phys_accumulator -= phys_dt;

            // update the physics
            update_grid(grid, grid2, phys_dt, phys_dx, phys_dy, D, x_min, x_max, y_min, y_max);
            
        }

        while (timeSinceLastUpdate >= timePerFrame) // render part
        {
            timeSinceLastUpdate -= timePerFrame;

            // draw the elements
            window.clear();
            draw_grid(grid);
            window.display();

        }

        sf::sleep(sf::milliseconds(1));

    }

    delete_grid(grid);
    delete_grid(grid2);

    return 0;

}