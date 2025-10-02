import numpy as np
import matplotlib.pyplot as plt

def inv(matrix):
    if np.linalg.matrix_rank(matrix) != matrix.shape[0]:
        raise ValueError("La matrice n'est pas inversible")
    
    n = len(matrix)
    inverse = np.identity(n)
    matrix = matrix.astype(float)
    
    for i in range(n):
        pivot = matrix[i][i]
        if pivot == 0:
            raise ValueError("La matrice n'est pas inversible")
        
        matrix[i] /= pivot
        inverse[i] /= pivot
        
        for j in range(n):
            if i != j:
                ratio = matrix[j][i]
                matrix[j] -= ratio * matrix[i]
                inverse[j] -= ratio * inverse[i]
    
    return inverse

b = 6.3e-5 #temps de demi-vie = 30.15 ans - unités en jour^-1
m = 1/2
t = 1/15
i = 1/120
p = 1/90
r = 1/10
x = 1/30
c = 1/2
s = 1/30
z = 1/30
e = 2.74e-4
dt = 1/50 # = 1/100 min(1/paramètre) = 1/50 

M = np.array([[1,b*dt,b*dt,b*dt,b*dt,b*dt,b*dt,b*dt,b*dt],
     [0,1-b*dt,0,0,s*dt,s*dt,0,0,0],
     [0,0,1-b*dt,0,0,0,0,0,e*dt],
     [0,0,0,1-(b+t+i+m)*dt,0,0,0,0,0],
     [0,0,0,t*dt,1-(b+s+c)*dt,0,0,0,0],
     [0,0,0,0,c*dt,1-(b+s+z)*dt,0,0,0],
     [0,0,0,m*dt,0,0,1-(b+r)*dt,p*dt,0],
     [0,0,0,0,0,0,r*dt,1-(b+p+x)*dt,0],
     [0,0,0,i*dt,0,z*dt,0,x*dt,1-(b+e)*dt]])   #matrice canonique de transition dans l'ordre B.SEATCMPH

R = np.array([[b*dt,b*dt,b*dt,b*dt,b*dt,b*dt,b*dt,b*dt]])

Q = np.array([[1-b*dt,0,0,s*dt,s*dt,0,0,0],
     [0,1-b*dt,0,0,0,0,0,e*dt],
     [0,0,1-(b+t+i+m)*dt,0,0,0,0,0],
     [0,0,t*dt,1-(b+s+c)*dt,0,0,0,0],
     [0,0,0,c*dt,1-(b+s+z)*dt,0,0,0],
     [0,0,m*dt,0,0,1-(b+r)*dt,p*dt,0],
     [0,0,0,0,0,r*dt,1-(b+p+x)*dt,0],
     [0,0,i*dt,0,z*dt,0,x*dt,1-(b+e)*dt]])

A = np.dot(R,inv(np.identity(8)-Q)) # matrice d'absorbance

Meq = np.block([[np.identity(1),A],[np.zeros((8,1)),np.zeros((8,8))]])

#T = inv(np.identity(8)-Q) * dt #temps moyen qui sera passé en j étant en i

#tau = np.dot(np.transpose(T),np.array([[1],[1],[1],[1],[1],[1],[1],[1]])) #temps qui sera encore passé dans les états de transition avant absorption

n0 = np.array([[0],[0],[0],[1],[0],[0],[0],[0],[0]])

"""
neq = np.dot(Meq,n0)

def scdgrandabs (L) :
    M = [abs(x) for x in L]
    for k in range(0,len(M)) :
        if M[k] == max(M) :
            M[k] = 0
    return (max(M))

lambda2 = scdgrandabs(np.linalg.eigvals(M))

def v_conv (t) :
    return lambda2**(t/dt)

def v_conv_t () :
    X = np.linspace(0,100000,int(100000/dt))
    Y = v_conv(X)
    plt.plot(X,Y)
    plt.show()
"""

def n(t) :
    return np.dot(np.linalg.matrix_power(M,int(t/dt)),n0)

dt = 1 # on prend dt plus grand pour des soucis de calculs

X = np.linspace(0,100000,int(100000/dt)) 
Y = [n(int(x)) for x in X]

def select (M,k) : # k dans [0,8]
    L = []
    for i in range (0,len(M)) :
        L.append(M[i][k])
    return L

Y1 = select(Y,0)
Y2 = select(Y,1)
Y3 = select(Y,2)
Y4 = select(Y,3)
Y5 = select(Y,4)
Y6 = select(Y,5) #C
Y7 = select(Y,6)
Y8 = select(Y,7) #P
Y9 = select(Y,8)

plt.plot(X,Y1,label="B")
plt.plot(X,Y2,label="S")
plt.plot(X,Y3,label="E")
plt.plot(X,Y4,label="A")
plt.plot(X,Y5,label="T")
plt.plot(X,Y6,label="C")
plt.plot(X,Y7,label="M")
plt.plot(X,Y8,label="P")
plt.plot(X,Y9,label="H")
plt.legend()
plt.show()

dt = 1/50

def dHc(t) :
    return z*dt*n(t)[5][0]

def dHp(t) :
    return x*dt*n(t)[7][0]

def Hc() : 
    s=0
    t=0
    while t<=500: #T temps pour que l'équilibre pour H s'installe. On prend T = dernière valeur de la liste X
        s+=dHc(t)
        t+=dt
    return s

def Hp() :
    s=0
    t=0
    while t<=500:
        s+=dHp(t)
        t+=dt
    return s

print("la contribution de Césium des poissons aux humains est de",Hp(),", tandis que celle des végétaux est de ",Hc())

M2 = np.array([[1,0,0,b*dt,b*dt,b*dt,b*dt,b*dt,b*dt],
      [0,1,0,0,i*dt,0,z*dt,0,0],
      [0,0,1,0,i*dt,0,0,0,x*dt],
      [0,0,0,1-b*dt,0,s*dt,s*dt,0,0],
      [0,0,0,0,1-(b+m+t+i)*dt,0,0,0,0],
      [0,0,0,0,t*dt,1-(s+b+c)*dt,0,0,0],
      [0,0,0,0,0,c*dt,1-(z+b+s)*dt,0,0],
      [0,0,0,0,m*dt,0,0,1-(b+p)*dt,r*dt],
      [0,0,0,0,0,0,0,p*dt,1-(b+x+r)*dt]]) #BHcHp.SATCMP

R2 = np.array([[b*dt,b*dt,b*dt,b*dt,b*dt,b*dt],
               [0,i*dt,0,z*dt,0,0],
               [0,i*dt,0,0,0,x*dt]])

Q2 = np.array([[1-b*dt,0,s*dt,s*dt,0,0],
               [0,1-(b+m+t+i)*dt,0,0,0,0],
               [0,t*dt,1-(s+b+c)*dt,0,0,0],
               [0,0,c*dt,1-(z+b+s)*dt,0,0],
               [0,m*dt,0,0,1-(b+p)*dt,r*dt],
               [0,0,0,0,p*dt,1-(b+x+r)*dt]])

A2 = np.dot(R2,inv(np.identity(6)-Q2))

Meq2 = np.block([[np.identity(3),A2],[np.zeros((6,3)),np.zeros((6,6))]])

n02 = np.array([[0],[0],[0],[0],[1],[0],[0],[0],[0]])

neq2 = np.dot(Meq2,n02)

print ("la probabilité de finir en Hc ie la proportion de Cesium nous atteignant si on stoppait la consommation de poisson est",neq2[1][0],"tandis que la proportion de Cesium si on stoppait la consommation des végétaux est",neq2[2][0])
# justifiable car après avoir atteint l'homme, le Cesium se désintègre indépendemment du chemin suivi