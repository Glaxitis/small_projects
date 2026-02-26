#include <SFML/Graphics.hpp>
#include <complex>
#include <iostream>

int n = 500;

unsigned int WIDTH = 1920; unsigned int HEIGHT = 1080;
int CELL_SIZE = 1;
int ROWS = HEIGHT/CELL_SIZE; int COLS = WIDTH/CELL_SIZE;

sf::RenderWindow window(sf::VideoMode({WIDTH, HEIGHT}), "Mandelbrot");

void inv_transf(double& x, double& y, double x_min, double x_max, double y_min, double y_max) // transforme la coordonnée d'un pixel en la coordonnée absolue
{
    x = x_min + (x_max - x_min) * x / double(WIDTH);
    y = y_min + (y_max - y_min) * (double(HEIGHT) - y) / double(HEIGHT);
}

void suite(std::complex<double>& u, std::complex<double> c)
{
    u = u * u + c; 
}

std::complex<double> suite_iter_n(int n, std::complex<double> c)
{
    std::complex<double> u = (0.0, 0.0);
    for (int k = 1 ; k<=n ; ++k)
    {        
        suite(u, c);
        if (std::norm(u) >= 2)
        {
            u = (0.0, 0.0);
            break;
        }
    }    
    return u;
}

double** set_grid()
{
    double** grid = new double*[ROWS];
    for (int row = 0 ; row < ROWS ; ++row)
    {
        grid[row] = new double[COLS];
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

void get_grid(double** grid, double x_min = -2, double x_max = 1, double y_min = -1, double y_max = 1)
{
    for (int row=0; row<ROWS; ++row)
    {
        for (int col=0; col<COLS; ++col)
        {
            double x = col * CELL_SIZE;
            double y = row * CELL_SIZE;
            inv_transf(x, y, x_min, x_max, y_min, y_max);
            std::complex<double> c(x, y);
            std::complex<double> u = suite_iter_n(n, c);
            grid[row][col] = std::norm(u);
        }
    }
}

sf::Color color_shade(double x) // 0 <= x <= 2 : 0 white, 2 black
{
    int intensity = int((2-x) / 2 * 255);
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
    double** grid = set_grid();
    get_grid(grid, -0.4, 0, 0.5, 1);

    window.clear();
    draw_grid(grid);
    window.display();

    while (window.isOpen())
    {
        while (const std::optional event = window.pollEvent())
        {
            if (event -> is <sf::Event::Closed>())
                window.close();
        }
    }
    delete_grid(grid);
    return 0;
}