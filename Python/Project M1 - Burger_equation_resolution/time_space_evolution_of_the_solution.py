import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import solve_banded

# very viscous v=1, dx=0.1
# viscous v=0.1, dx=0.05
# weakly viscous v=0.01, dx=0.01

v=0.01 # viscosity
dt=0.0001 # time step
t_tot=2 # total time
N=int(t_tot/dt) # number of steps in time

L=2 # length
dx=0.01 # step in space
n=int(L/dx) # number of steps in space
intX=[k*dx for k in range(int(L/dx)-1)] # space interval

t=0

maindiagK=np.empty(n-1) # matrix K
offdiagK=np.empty(n-2)
for i in range(n-1):
    maindiagK[i]=2*dx/3
for i in range(n-2):
    offdiagK[i]=dx/6   
K=np.diag(offdiagK, -1) + np.diag(maindiagK) + np.diag(offdiagK, 1) # construction of K

ab=np.array([ # pour l'inversion de K
    [offdiagK[0] for k in range(n-1)],
    [maindiagK[0] for k in range(n-1)],
    [offdiagK[0] for k in range(n-1)]
])
ab[0][0]=0
ab[2][n-2]=0
b=np.zeros(n-1)

maindiagM=np.empty(n-1) # matrix M
offdiagM=np.empty(n-2)
for i in range(n-1):
    maindiagM[i]=2/dx
for i in range(n-2):
    offdiagM[i]=-1/dx  
M=np.diag(offdiagM, -1) + np.diag(maindiagM) + np.diag(offdiagM, 1) # construction of M

def P(i,j,k): # "matrix" P
    if i==j==k:
            return 0
    elif i==j and abs(k-i)==1:
            return (k-i)/3
    elif j==k and abs(i-j)==1:
            return (j-i)/6
    elif i==k and abs(j-i)==1:
            return (i-j)/6
    else:
        return 0

T=[t]
U=np.zeros((n-1, N)) # local velocity of the fluid - each line for n, each column for t
for i in range(n-1):
    U[i][0]=np.sin(np.pi*i*dx) # initial state at t=0

fig, ax = plt.subplots(1, 2, figsize=(12, 5))

u0=np.zeros(len(intX)) # plot the initial state at t=0
for k in range(1,n-1):
    u0[k]=u0[k]+U[k][0]
ax[0].plot(intX,u0)
ax[0].set_xlim(0,2)
ax[0].set_xlabel('Time')
ax[0].set_ylabel('Space')

for k in range(1,N):
    t+=dt
    T.append(t)
    i=0 # particular case 1
    b[0]=-v*(M[i][i]*U[i][k-1]+M[i][i+1]*U[i+1][k-1])-(P(i,i,i)*U[i][k-1]*U[i][k-1]+P(i,i,i+1)*U[i][k-1]*U[i+1][k-1]+P(i,i+1,i)*U[i+1][k-1]*U[i][k-1]+P(i,i+1,i+1)*U[i+1][k-1]*U[i+1][k-1])
    i=n-2 # particular case 2
    b[n-2]=-v*(M[i][i-1]*U[i-1][k-1]+M[i][i]*U[i][k-1])-(P(i,i-1,i-1)*U[i-1][k-1]*U[i-1][k-1]+P(i,i-1,i)*U[i-1][k-1]*U[i][k-1]+P(i,i,i-1)*U[i][k-1]*U[i-1][k-1]+P(i,i,i)*U[i][k-1]*U[i][k-1])
    for i in range(1,n-2): # general case
        b[i]=-v*(M[i][i-1]*U[i-1][k-1]+M[i][i]*U[i][k-1]+M[i][i+1]*U[i+1][k-1])-(P(i,i-1,i-1)*U[i-1][k-1]*U[i-1][k-1]+P(i,i-1,i)*U[i-1][k-1]*U[i][k-1]+P(i,i,i-1)*U[i][k-1]*U[i-1][k-1]+P(i,i,i)*U[i][k-1]*U[i][k-1]+P(i,i,i+1)*U[i][k-1]*U[i+1][k-1]+P(i,i+1,i)*U[i+1][k-1]*U[i][k-1]+P(i,i+1,i+1)*U[i+1][k-1]*U[i+1][k-1])
    r=solve_banded((1,1),ab,b) # solve the equation
    for i in range(n-1):
        U[i][k]=U[i][k-1]+r[i]*dt # updating U at the new time
    if k%1000==0: # plotting some curves during the evolution
        u1=np.zeros(len(intX))
        for j in range(1,n-1):
            u1[j]=u1[j]+U[j][k]
        ax[0].plot(intX,u1)

imshow=ax[1].imshow(U, extent=[0, t_tot, 0, L], aspect='auto', cmap='viridis', origin='lower')
plt.colorbar(imshow,label='Amplitude of U')
ax[1].set_xlabel('Time')
ax[1].set_ylabel('Space')
ax[1].set_title('Evolution of U(x, t)')
plt.show()