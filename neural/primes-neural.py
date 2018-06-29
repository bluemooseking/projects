# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt


# Get data
#df = pd.read_csv('primes.data.csv', names=range(20), engine='c')
#X = df.loc[:, 0:0]
#y = df.loc[:, 1:1]
# Create sets
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.02)
#X_dev, X_test, y_dev, y_test = train_test_split(X_test, y_test, test_size=0.5)

np.random.seed(3)
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

def initialize_parameters(X, dims, Y):
    parameters = {}
    dims.insert(0, X.shape[0])
    dims.append(Y.shape[0])
    L = len(dims)
    
    for l in range(1, L):
        parameters['W' + str(l)] = np.random.randn(dims[l], dims[l-1]) * 0.01
        parameters['b' + str(l)] = np.zeros((dims[l], 1))
        
        assert (parameters['W' + str(l)].shape == (dims[l], dims[l-1]))
        assert (parameters['b' + str(l)].shape == (dims[l], 1))
        
    return parameters

def linear_forward(A, W, b):
    Z = np.dot(W, A) + b
    assert(Z.shape == (W.shape[0], A.shape[1]))
    cache = (A, W, b)
    return Z, cache

def sigmoid(Z):
    A = 1 / (1 + np.exp(-Z))
    assert(A.shape == Z.shape)
    cache = (Z)
    return A, cache

def dsigmoid(dA, activation_cache):
    Z = activation_cache
    gprimeZ = np.exp(-Z) / np.power(1 + np.exp(-Z), 2)
    dZ = np.multiply(dA, gprimeZ)
    assert(dZ.shape == dA.shape)
    return dZ
  
def relu(Z):
    A = np.multiply(Z, (Z>0))
    assert(A.shape == Z.shape)
    cache = (Z)
    return A, cache

def drelu(dA, activation_cache):
    Z = activation_cache
    gprimeZ = (Z > 0)
    dZ = np.multiply(dA, gprimeZ)
    assert(dZ.shape == dA.shape)
    return dZ
    
def linear_activation_forward(A_prev, W, b, activation):    
    if activation == "sigmoid":
        Z, linear_cache = linear_forward(A_prev, W, b)
        A, activation_cache = sigmoid(Z)
        
    elif activation == "relu":
        Z, linear_cache = linear_forward(A_prev, W, b)
        A, activation_cache = relu(Z)
        
    assert(A.shape == (W.shape[0], A_prev.shape[1]))
    cache = (linear_cache, activation_cache)
    
    return A, cache

def forward_prop(X, parameters):
    caches = []
    A = X
    L = len(parameters) // 2
    
    for l in range(1, L):
        A_prev = A
        A, cache = linear_activation_forward(A_prev, parameters['W' + str(l)], parameters['b' + str(l)], 'sigmoid')
        caches.append(cache)
        
    AL, cache = linear_activation_forward(A, parameters['W' + str(L)], parameters['b' + str(L)], 'sigmoid')
    caches.append(cache)
    
    assert(AL.shape == (1, X.shape[1]))
    return AL, caches
    
def compute_cost(AL, Y):
    m = Y.shape[1]
    cost = (-1 / m) * np.sum(np.multiply(Y, np.log(AL)) + np.multiply(1-Y, np.log(1-AL)))
    cost = np.squeeze(cost)
    assert(cost.shape == ())
    return cost

def linear_backward(dZ, cache):
    A_prev, W, b, = cache
    m = A_prev.shape[1]
    
    dW = (1/m) * np.dot(dZ, A_prev.T)
    db = (1/m) * np.sum(dZ, axis = 1, keepdims = True)
    dA_prev = np.dot(W.T, dZ)
    
    assert(dA_prev.shape == A_prev.shape)
    assert(dW.shape == W.shape)
    assert(db.shape == b.shape)
    
    return dA_prev, dW, db

def linear_activation_backward(dA, cache, activation, gradient_check = False):
    linear_cache, activation_cache = cache
    
    if activation == "relu":
        dZ = drelu(dA, activation_cache)
        
    elif activation == "sigmoid":
        dZ = dsigmoid(dA, activation_cache)
        
    dA_prev, dW, db = linear_backward(dZ, linear_cache)
    
    '''
    if gradient_check:
        epsilon = 1e-7
        theta = activation_cache
        if activation == "relu"
            
            
        
        elif activation == "sigmoid"
    '''
    
    return dA_prev, dW, db, dZ

def backward_prop(AL, Y, caches):
    grads = {}
    L = len(caches)
    m = AL.shape[1]
    Y = Y.reshape(AL.shape)
    
    grads['dAL'] = - (np.divide(Y, AL) - np.divide(1-Y, 1-AL))
    
    current_cache = caches[L-1]
    grads['dA' + str(L)], grads['dW' + str(L)], grads['db' + str(L)], grads['dZ' + str(L)] = linear_activation_backward(grads['dAL'], current_cache, "sigmoid")
    
    for l in reversed(range(L-1)):
        current_cache = caches[l]
        dA_prev_temp, dW_temp, db_temp, dZ_temp = linear_activation_backward(grads['dA' + str(l+2)], current_cache, "sigmoid")
        grads['dA' + str(l+1)] = dA_prev_temp
        grads['dW' + str(l+1)] = dW_temp
        grads['db' + str(l+1)] = db_temp
        grads['dZ' + str(l+1)] = dZ_temp
        
    return grads

def update_parameters(parameters, grads, learning_rate):
    L = len(parameters) // 2
    
    for l in range(1, L+1):
        parameters['W' + str(l)] -= learning_rate * grads['dW' + str(l)]
        parameters['b' + str(l)] -= learning_rate * grads['db' + str(l)]
        
    return parameters

def build_neural_model(X, Y, hidden_dims = [], learning_rate = 0.01, num_iterations = 3000, print_cost = False):
    costs = []
    parameters = initialize_parameters(X, hidden_dims, Y)
    
    for i in range(0, num_iterations):
        
        AL, caches = forward_prop(X, parameters)
        cost = compute_cost(AL, Y)
        grads = backward_prop(AL, Y, caches)
        parameters = update_parameters(parameters, grads, learning_rate)
        
        if print_cost:
            costs.append(cost)
            if i % 100 == 0:
                print("Cost after iteration %i: %f" %(i, cost))
        
    if print_cost:
        plt.plot(np.squeeze(costs))
        plt.ylabel('cost')
        plt.xlabel('interations')
        plt.title('Learning rate = ' + str(learning_rate))
        plt.show()
    
    return parameters

def predict(X, parameters):
    AL, _ = forward_prop(X, parameters)
    return AL

parameters = build_neural_model(X.T, y.T, [4], num_iterations = 20000, print_cost = True)
print(predict(X.T, parameters))