#define _USE_MATH_DEFINES
#include <iostream>
#include <math.h>
#include <iomanip>
#include <SFML/Graphics.hpp>

unsigned int WIDTH = 820; unsigned int HEIGHT = 820;

sf::RenderWindow window(sf::VideoMode({WIDTH, HEIGHT}), "Pendulum");

const double g = 9.81;
const double L = 1.0;
const double w2 = g/L;
const double theta0 = M_PI/3.;
const double phys_dt = 0.01;

double f1(double dtheta) // equa diff 1 : d(theta)/dt = dtheta
{
    return dtheta;
}

double f2(double theta)
{
    return ( - w2 * std::sin(theta) ); // equa diff 2 : d(dtheta)/dt + w² sin(theta) = 0
}

void RK4(double& theta, double& dtheta, double dt) // resolution by RK4 method
{
    double k1, k2, k3, k4;
    double l1, l2, l3, l4;
    k1 = dt*f1(dtheta);
    l1 = dt*f2(theta);
    k2 = dt*f1(dtheta + 0.5 * l1);
    l2 = dt*f2(theta + 0.5 * k1);
    k3 = dt*f1(dtheta + 0.5 * l2);
    l3 = dt*f2(theta + 0.5 * k2);
    k4 = dt*f1(dtheta + l3);
    l4 = dt*f2(theta + k3);
    theta += (k1+2*k2+2*k3+k4)/6.0;
    dtheta += (l1+2*l2+2*l3+l4)/6.0;
}

int main()
{

    // render quantities

    const int TARGET_FPS = 60;
    const sf::Time timePerFrame = sf::seconds(1.0f / TARGET_FPS);
    sf::Clock clock;
    sf::Time timeSinceLastUpdate = sf::Time::Zero;

    // origins and initial values

    double fact = 400.f; // scale factor physics -> displayed
    double x0 = 1; // coordinates of the fixed mass
    double y0 = 0.5;

    double theta = theta0; // initial angle
    double dtheta = 0.; // initial angular velocity
    float phys_accumulator = sf::Time::Zero.asSeconds(); // accumulated physical time 

    // define the ball and the line

    sf::CircleShape circle(30.0f);
    circle.setFillColor(sf::Color::Black);

    sf::RectangleShape line({1.f, float(fact * L)});
    line.setFillColor(sf::Color::White);
    line.setPosition({float(fact * x0 + 15.), float(fact * y0 + 10.)});

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
            
            RK4(theta, dtheta, phys_dt);

        }

        while (timeSinceLastUpdate >= timePerFrame) // render part
        {

            timeSinceLastUpdate -= timePerFrame;

            // update the elements
            
            circle.setPosition({float(fact * (x0 + L*std::sin(theta)) - 15.), float(fact * (y0 + L*std::cos(theta)) - 15.)});
            line.setRotation(sf::radians(- theta));

            // draw the elements

            window.clear(sf::Color(150,150,150,255));
            window.draw(line);
            window.draw(circle);
            window.display();
            
        }

        sf::sleep(sf::milliseconds(1));

    }

    return 0;

}