import numpy as np
import matplotlib.pyplot as plt
from qiskit.circuit.library import TwoLocal
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
import random as rd

g0 = -0.4804
g1 = 0.3435
g2 = g1
g3 = 0.0906
g4 = 0.1286
g5 = g4
coefs = np.array([g0,g1,g2,g3,g4,g5])

alpha0 = 1
alpha1 = alpha0
alpha2 = alpha0
rho = 0.9
rho2 = 1.1
c = 0.1
c1 = 1e-4
c2 = 0.9
N = 20

ansatz = TwoLocal(2, 'ry', 'cx', 'linear', reps=1, insert_barriers=False)
num_parameters = ansatz.num_parameters
parameters0 = np.array([2*np.pi*rd.random() for _ in range(num_parameters)])
parameters1 = parameters0.copy()
parameters2 = parameters1.copy()

H = SparsePauliOp(["II", "ZI", "IZ", "ZZ", "XX", "YY"], coefs)

estimator = StatevectorEstimator()

def expectation_H(parameters):
    parametred_circuit = ansatz.assign_parameters(parameters)
    return estimator.run([(parametred_circuit, H)]).result()[0].data.evs

def grad_H(parameters):
    grad_H = np.zeros_like(parameters)
    for i in range(num_parameters):
        params_plus = parameters.copy()
        params_plus[i] += np.pi/2
        params_minus = parameters.copy()
        params_minus[i] -= np.pi/2
        grad_H[i] = 0.5 * (expectation_H(params_plus) - expectation_H(params_minus))
    return grad_H

def new_parameters(parameters, alpha, grad):
    return parameters - alpha * grad

def update_alpha1(parameters, grad, expectation):
    alpha = alpha0
    while (expectation_H(new_parameters(parameters,alpha,grad)) > expectation - c*alpha*np.dot(grad,grad)):
        alpha *= rho
    return alpha

def update_alpha2(parameters, grad, expectation, direction):
    alpha = alpha0
    count = 0
    while True:
        count += 1
        if expectation_H(parameters + alpha * direction) > expectation + c1 * alpha * np.dot(grad, direction): ## Wolfe conditions not respected
            alpha *= rho
        elif np.dot(grad_H(parameters + alpha * direction), direction) < c2 * np.dot(grad, direction): 
            alpha *= rho2
        else:
            break
        if alpha > 1e+5 :
            break
    return alpha

def update_hess(hess, s, y): # commputation of the inverse hessian s.t. M_k s_k-1 = y_k-1
    ys = np.dot(y,s)
    if ys < 1e-8 :
        return hess
    return (hess + (1 + (np.dot(y,np.matmul(hess,y))) / ys) * np.outer(s, s) / ys - (np.matmul(hess,np.outer(y, s)) + np.matmul(np.outer(s, y),hess)) / ys) # BFGS method

hess = np.eye(num_parameters)
grad2 = grad_H(parameters2)

expectation0 = 0
expectation1 = expectation0
expectation2 = expectation0

T = []
EXP0 = []
EXP1 = []
EXP2 = []

for k in range(N):

    print(round(k/N * 100, 3), '%')

    grad0 = grad_H(parameters0)
    grad1 = grad_H(parameters1)
    grad2 = grad2.copy()

    direction = - np.matmul(hess, grad2)

    expectation0 = expectation_H(parameters0)
    expectation1 = expectation_H(parameters1)
    expectation2 = expectation_H(parameters2)

    alpha1 = update_alpha1(parameters1, grad1, expectation1)
    alpha2 = update_alpha2(parameters2, grad2, expectation2, direction)

    parameters2_new = parameters2 + alpha2 * direction
    grad2_new = grad_H(parameters2_new)
    hess = update_hess(hess, parameters2_new-parameters2, grad2_new - grad2)
    if np.dot(grad2, direction) >= 0: # not decreasing anymore -> reset hessian
        hess = np.eye(num_parameters)
        direction = -grad2

    parameters0 = new_parameters(parameters0, alpha0, grad0)
    parameters1 = new_parameters(parameters1, alpha1, grad1)
    parameters2 = parameters2_new
    grad2 = grad2_new

    T.append(k+1)
    EXP0.append(expectation0)
    EXP1.append(expectation1)
    EXP2.append(expectation2)

plt.figure(figsize=(10, 6))
plt.scatter(T, EXP0, label='constant alpha')
plt.scatter(T, EXP1, label='Armijo alpha')
plt.scatter(T, EXP2, label='BFGS + Wolf alpha')

plt.text(T[-1]+0.2, EXP0[-1], f"{EXP0[-1]:.3f}", fontsize=9, color='blue')
plt.text(T[-1]+0.2, EXP1[-1], f"{EXP1[-1]:.3f}", fontsize=9, color='orange')
plt.text(T[-1]+0.2, EXP2[-1], f"{EXP2[-1]:.3f}", fontsize=9, color='green')

plt.title('Evolution of the ground state of the H2 hamiltonian')
plt.ylabel('ground state energy')
plt.xlabel('number of iterations')

plt.ylim(-1.15,0)
plt.axhline(-1.137,0,N)

plt.legend()
plt.show()