import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import solve_banded
from matplotlib.animation import FuncAnimation
from scipy.integrate import quad
from functools import partial
plt.style.use('seaborn-v0_8-pastel')

def produit(kb, u):  # transformer K.u en produit avec kb
    n = len(u)
    result = np.zeros(n)
    # Diagonale principale
    result += kb[1, :] * u
    # Sur-diagonale
    result[:-1] += kb[0, 1:] * u[1:]
    # Sous-diagonale
    result[1:] += kb[2, :-1] * u[:-1]
    return result

# Parameters ###########################################
L = 2  # Length of the domain
nu = 0.01  # Viscosity
t0 = 0
tf = 10  # Final time
ntimestep = 1000
dt = (tf - t0) / ntimestep  # Time step
n = 75  # Number of spatial elements
h = L / n  # Spatial step

# Basis function ######################################
def fun(x, i):
    return np.piecewise(x, [x < (i - 1) * h, 
                            ((i - 1) * h <= x) & (x <= i * h),
                            (i * h < x) & (x <= (i + 1) * h),
                            x > (i + 1) * h],
                        [0, (x - (i - 1) * h) / h, -(x - (i + 1) * h) / h, 0])

def P(i,j,k):
    if 0<=i<=n-1 and 0<=j<=n-1 and 0<=k<=n-1:
        if i==j==k:
            return 0
        elif i==j and abs(k-i)==1:
            return (k-i)/3
        elif j==k and abs(i-j)==1:
            return (j-i)/6
        elif i==k and abs(j-i)==1:
            return (i-j)/6
    return 0

# Matrices ############################################
maindiagm = (2 / 3) * h * np.ones(n - 1)
offdiagm = (1 / 6) * h * np.ones(n - 2)
mb = np.zeros((3, n - 1))
mb[1] = maindiagm
mb[0, 1:] = offdiagm
mb[2, :-1] = offdiagm

maindiagk = (2 / h) * np.ones(n - 1)
offdiagk = (-1 / h) * np.ones(n - 2)
kb = np.zeros((3, n - 1))
kb[1] = maindiagk
kb[0, 1:] = offdiagk
kb[2, :-1] = offdiagk

# Initial condition ###################################
def psi(x):
    return np.sin(np.pi * x)

y0 = np.array([psi((i + 1) * h) for i in range(n - 1)])

# Solver ##############################################
def solve_burgers_all_steps():
    y = np.copy(y0)
    solutions = [y.copy()]  # Stocker toutes les solutions

    for _ in range(ntimestep):
        # Compute the nonlinear term
        nonlinear = np.zeros(n - 1)
        for j in range(n-1):
            for i in range(max(j-1,0),min(j+1,n-2)+1):
                for k in range(max(j-1,0),min(j+1,n-2)+1):
                    nonlinear[j] += y[i] * y[k] * P(i,j,k)
        rhs = -nu * produit(kb, y) - nonlinear
        dy = solve_banded((1, 1), mb, rhs)
        y += dt * dy
        solutions.append(y.copy())  # Ajouter la solution à la liste

    return solutions

# Pré-calcul des solutions ###########################
solutions = solve_burgers_all_steps()

# Animation ###########################################
fig, ax = plt.subplots()
ax.set_xlim(0, L)
ax.set_ylim(-1, 1)
line, = ax.plot([], [], lw=2)

def init():
    line.set_data([], [])
    return line,

def animate(frame):
    t = frame * dt
    y = solutions[frame]
    x = np.linspace(0, L, 101)
    approx = [sum(y[i] * fun(xi, i + 1) for i in range(n - 1)) for xi in x]
    line.set_data(x, approx)
    return line,

anim = FuncAnimation(fig, animate, init_func=init, frames=ntimestep, interval=20, blit=True)
plt.show()
