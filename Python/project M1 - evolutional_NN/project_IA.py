import matplotlib.pyplot as plt
import numpy as np
import random as rd
from heapq import nsmallest

Nloop = 500
b = 5 # number of hidden neurons
n = 15 # number of trained dots
k = 3 # number of selected dots (the best dots)
r = 10 # number of obstacles
d = 15 # distance from r=(0,0) to to where to place the obstacles (in practical near the goal)
D = 10 # height where the obstacles will be placed
N = 400 # number of steps in time
dt = 0.01 # time step
t = 0 # initial time
time = [t]
v = np.array([1,0]) # initial speed for all
pos = np.array([0,0]) # initial position for all

class Dot: # class of the different points following a trajectory given by the NN

    def __init__(self, weight1, weight2):
        self.weight1 = weight1 # weight from input layer to hidden layer
        self.weight2 = weight2 # weight from hidden layer to output layer
        self.set_pos = np.array([pos]) # array of the different positions of the trajectory
        self.set_velocity = np.array([v]) # array of velocities along the trajectory
        self.distance = 20 # initial distance from the goal

class Circle: # class of circles containing obstacles (green) and the objective (yellow)

    def __init__(self, coordinates, radius, goal = False):
        self.radius = radius # spherical obstacle/goal
        self.coordinates = coordinates
        self.list = np.array([coordinates[0],coordinates[1]]) # coordinates in the form of a list
        if not goal:
            self.color = (0,1,0,0.3)
        if goal:
            self.color = (1,1,0,0.5)

set_dots = np.array([Dot(2-4*np.random.rand(b,r+1), 2-4*np.random.rand(3,b)) for _ in range(n)]) # set of the points that will form a trajectory
set_obstacles = np.array([Circle((-d + 2 * d*rd.random(),-D + 2*D*rd.random()), 0.5 + rd.random()/2) for _ in range(r-1)]) # set of obstacles
set_obstacles = np.append(set_obstacles, Circle((5,0), 0.5 + rd.random()/2)) # add an obstacle in front of the initial dots for more interesting behaviour
goal = Circle((20,0), 5, True)

def norm(v): # returns the norm of the vector v
    return np.sqrt(v[0]**2+v[1]**2)

def act(x): # activation function
    return (1/(1+np.exp(-x))) # results between 0 and 1

def NN(sigma, weight1, weight2): # sigma and weight np.array of the initial states (distance from obstacle, arrival)
    s = act(np.dot(weight1, sigma))
    S = act(np.dot(weight2, s))
    return S # output of numbers between 0 and 1 (abs, dux, duy)

def speed(abs, dux, duy, v): # given the previous velocity and the results of the NN, gives the next velocity
    u = v/norm(v)
    u[0] = u[0] + dux
    u[1] = u[1] + duy
    u = u/norm(u)
    vnew = abs*u
    return vnew

def evolution(set_dots, set_obstacles, goal, t = 0): # for a given simulation (loop), states the behaviour of the dots
    for _ in range(N): # time loop
        u = 0
        for _ in range(len(set_dots)): # dots loop
            if u >= len(set_dots): # since len(set_dots) varies
                break
            dot = set_dots[u]
            v = dot.set_velocity[-1] # last registered velocity
            pos = dot.set_pos[-1] # last registered position
            sigma = np.array([]) # input
            for obstacle in set_obstacles: # obstacles loop
                dist = norm(pos - obstacle.list) # distance of the dot w.r.t. the obstacles
                sigma = np.append(sigma, dist) # add to the inputs
                if dist <= obstacle.radius:
                    set_dots = np.delete(set_dots, u) # remove the dots crossing the obstacles (the dots are not allowed to do so)
            dist = norm(goal.list - pos) # distance from the goal
            dot.distance = dist
            sigma = np.append(sigma, dist) # add to the inputs
            weight1 = dot.weight1
            weight2 = dot.weight2
            (abs, dux, duy) = NN(sigma, weight1, weight2) # find the new velocity given the NN
            abs *= 10 # norm of velocity
            dux = 2*dux - 1 # x direction change
            duy = 2*duy - 1 # y direction change
            v = speed(abs, dux, duy, v)
            pos = pos + v*dt # update position
            dot.set_velocity = np.vstack((dot.set_velocity, v))
            dot.set_pos = np.vstack((dot.set_pos, pos))
            u += 1
        t += dt
        time.append(t)
    return set_dots # returns all the caracteristics of the dots during that simulation

def sort(k, arr): # returns the k smallest values of an array arr and their indices in arr
    indexed = [(value, index) for index, value in enumerate(arr)]
    smallest_pairs = nsmallest(k, indexed)  # Built-in Python, ultra-optimized, gets the k smallest elements among n in arr
    values = [x[0] for x in smallest_pairs]
    indices = [x[1] for x in smallest_pairs]
    return values, indices  

def select(L, k): # L matrix of all the n dots, selects the k best dots scores
    M = [dot.distance for dot in L]
    l, IND = sort(k, M)
    return IND, M # list of the indices of the genetically selected dots distances, as well as the matrix corresponding to the values of distances of each dot

def new_selection(l,k): # l list of all the n dots
    IND,J = select(l,k)
    L = []
    for j in IND:
        L.append(l[j])
    M = np.array([])
    for _ in range(n):
        p = rd.randint(0,k-1)
        q = rd.randint(0,k-1)
        (dot1, dot2) = (L[p], L[q])
        (weight1_dot1, weight2_dot1) = (dot1.weight1, dot1.weight2)
        (weight1_dot2, weight2_dot2) = (dot2.weight1, dot2.weight2)
        weight1_child = 1/2 * (weight1_dot1 + weight1_dot2) + 1 * (2 * np.random.rand(b,r+1) - 1) # mean + noise
        weight2_child = 1/2 * (weight2_dot1 + weight2_dot2) + 1 * (2 * np.random.rand(3,b) - 1)
        dot_child = Dot(weight1_child, weight2_child)
        M = np.append(M,dot_child)
    return M, J # list of new the n new dots that will be trained + list of the distances

def algo_gen(set_dots, set_obstacles, goal): # genetic algorithm that selects the best dots from the previous simulation
    x = [0] # list of the simulation number
    dist = np.array([20]) # list of the average distance of the dots from the goal for each simulation
    p = 1
    plt.ion()
    plt.figure(figsize=(10, 8))
    for i in range(Nloop - 1): # loop over the loops
        print(round(i/(Nloop) * 100, 2), '%')
        set_dots = evolution(set_dots, set_obstacles, goal) # set of dots for the simulation given the initial/previous data
        length = len(set_dots)
        
        if length == 0: # if every dot crosses an obstacle
            print('No valid dot')
        else:
            fig = plt.gcf() # displays the simulation
            fig.clf()
            ax = fig.gca()
            for j in range(length):
                print(j+1, "distance =", set_dots[j].distance)
                rx = []
                ry = []
                for [a,b] in set_dots[j].set_pos:
                    rx.append(a)
                    ry.append(b)
                plt.plot(rx,ry, color=(j/length, j/length, 1 - j/length))
                plt.xlim(-d,30)
                plt.ylim(-1.5*D,1.5*D)
            for obstacle in set_obstacles:
                circle = plt.Circle(obstacle.coordinates, obstacle.radius, color=obstacle.color)
                ax.add_patch(circle)
            goal_circle = plt.Circle(goal.coordinates, goal.radius, color=goal.color)
            ax.add_patch(goal_circle)
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.show()
            
        if length == 0: # if all the dots were crossing the obstacles
            pass
        set_dots, J = new_selection(set_dots, min(k,length)) # select the best distances
        x.append(p)
        dist = np.append(dist, np.mean(J))
        p += 1

    plt.ioff()
    set_dots = evolution(set_dots, set_obstacles, goal)
    _, J = new_selection(set_dots, min(k,length)) # select the best distances
    x.append(p)
    dist = np.append(dist, np.mean(J))
    return set_dots, x, dist

set_dots, x, dist = algo_gen(set_dots, set_obstacles, goal)

length = len(set_dots)
if length == 0: # if every dot crosses an obstacle
    print('No valid dot')
else: # displays the simulation
    fig = plt.gcf()
    fig.clf()
    for j in range(length):
        print(j+1, "distance =", set_dots[j].distance)
        rx = []
        ry = []
        for [a,b] in set_dots[j].set_pos:
            rx.append(a)
            ry.append(b)
        plt.plot(rx,ry, color=(j/length, j/length, 1 - j/length))
        plt.xlim(-d,30)
        plt.ylim(-1.5*D,1.5*D)
    ax = fig.gca()
    for obstacle in set_obstacles:
        circle = plt.Circle(obstacle.coordinates, obstacle.radius, color=obstacle.color)
        ax.add_patch(circle)
    goal_circle = plt.Circle(goal.coordinates, goal.radius, color=goal.color)
    ax.add_patch(goal_circle)
    plt.show()

plt.plot(x, dist, color='blue')
plt.xlabel('loops')
plt.ylabel('optimisation mean for goal')

plt.show()