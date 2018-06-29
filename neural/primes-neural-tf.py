# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

tf.reset_default_graph()

# Get data
df = pd.read_csv('analytic.data.csv', header=0, names=range(20), engine='c')
X = np.array(df.loc[1:, 0:0])
y = np.array(df.loc[1:, 4:4])

# Create sets
X_train, X_garbage, y_train, y_garbage = train_test_split(X, y, test_size=0.99)
X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.02)
X_dev, X_test, y_dev, y_test = train_test_split(X_test, y_test, test_size=0.5)

#np.random.seed(3)
#X_data = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
#y_data = np.array([[0], [1], [1], [0]])

def create_placeholders(n_x, n_y):
    X = tf.placeholder(tf.float32, shape = (n_x, None), name = 'X')
    Y = tf.placeholder(tf.float32, shape = (n_y, None), name = 'Y')
    return X, Y

def initialize_parameters(n_x, dims, n_y):
    parameters = {}
    dims.insert(0, n_x)
    dims.append(n_y)
    L = len(dims)
    
    for l in range(1, L):
        sWx = 'W' + str(l)
        sbx = 'b' + str(l)
        parameters[sWx] = tf.get_variable(sWx, [dims[l], dims[l-1]], initializer = tf.contrib.layers.xavier_initializer(seed=None))
        parameters[sbx] = tf.get_variable(sbx, [dims[l], 1], initializer = tf.zeros_initializer())
        
        assert (parameters[sWx].shape == (dims[l], dims[l-1]))
        assert (parameters[sbx].shape == (dims[l], 1))
        
    return parameters

def forward_prop(X, parameters):
    caches = {}
    Ax_prev = X
    L = len(parameters) // 2
    
    for l in range(1, L + 1):
        sWx = 'W' + str(l)
        sbx = 'b' + str(l)
        sZx = 'Z' + str(l)
        sAx = 'A' + str(l)
        caches[sZx] = tf.add(tf.matmul(parameters[sWx], Ax_prev), parameters[sbx])
        caches[sAx] = tf.nn.relu(caches[sZx])
        Ax_prev = caches[sAx]
    
    caches['ZL'] = sZx
    return caches
    
def compute_cost(caches, Y, parameters, beta):
    logits = tf.transpose(caches[caches['ZL']])
    labels = tf.transpose(Y)
    """
    cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(
            logits = logits,
            labels = labels
            ))
    """
    mse = tf.reduce_mean(tf.square(logits - labels))
    regularizer = 0
    for i in parameters:
        regularizer += tf.nn.l2_loss(parameters[i])
    cost = tf.reduce_mean(mse + beta * regularizer)
    assert(cost.shape == ())
    return cost

def random_mini_batches(X, Y, mb_size, seed = None):
    assert(X.shape[1] == Y.shape[1])
    
    minibatches = []
    
    if seed is not None:
        np.random.seed(seed)
    
    m = X.shape[1]
    rlist = np.arange(m)
    np.random.shuffle(rlist)
    
    rows = 1 + int(m / mb_size)
    full_list = np.resize(rlist,(rows, mb_size))
    final_row = np.delete(full_list[rows - 1], np.arange(m % mb_size, mb_size))
    full_list = np.delete(full_list, -1, 0)
    
    for sublist in full_list:
        minibatches.append((X[:, sublist], Y[:, sublist]))
    
    minibatches.append((X[:, final_row], Y[:, final_row]))
    return minibatches

def build_neural_model(X_train, Y_train, 
                       X_dev, Y_dev,
                       hidden_dims = [], 
                       learning_rate = 0.01,
                       reg_rate = 0.001,
                       num_epochs = 1500, 
                       minibatch_size = 32,
                       print_cost = False):
    costs = []
    (m, n_x) = X_train.shape
    (n, n_y) = Y_train.shape
    assert(m == n)
    
    print("X shape: %i, %i" % (m, n_x))
    print("Hidden Layers: " + str(hidden_dims))
    print("Y shape: %i, %i" % (n, n_y))
    print("Rates: alpha: %f beta: %f" % (learning_rate, reg_rate))
    print("Loops: mb_size: %i, epochs: %i" %(minibatch_size, num_epochs))
    print("Beginning Training...")
    
    X, Y = create_placeholders(n_x, n_y)
    parameters = initialize_parameters(n_x, hidden_dims, n_y)
    caches = forward_prop(X, parameters)
    cost = compute_cost(caches, Y, parameters, reg_rate)
    optimizer = tf.train.GradientDescentOptimizer(learning_rate = learning_rate).minimize(cost)
    init = tf.global_variables_initializer()
    
    with tf.Session() as sess:
        
        sess.run(init)
        
        for epoch in range(num_epochs + 1):
            
            epoch_cost = 0.
            num_minibatches = int(m / minibatch_size)
            minibatches = random_mini_batches(X_train.T, Y_train.T, minibatch_size)
            
            for minibatch in minibatches:
                
                (minibatch_X, minibatch_Y) = minibatch
                _, minibatch_cost = sess.run([optimizer, cost], 
                                         feed_dict={X: minibatch_X,
                                                    Y: minibatch_Y})
                epoch_cost += minibatch_cost / (num_minibatches + 1)
                
            if print_cost == True and epoch % 100 == 0:
                print ("Cost after epoch %i: %f" % (epoch, epoch_cost))
            if print_cost == True:
                costs.append(epoch_cost)
                
        
        if print_cost:
            plt.plot(np.squeeze(costs))
            plt.ylabel('cost')
            plt.xlabel('interations')
            plt.title('Learning rate = ' + str(learning_rate))
            plt.yscale('log')
            plt.show()
            
        parameters = sess.run(parameters)
        print ('Parameters have been trained')
        
        correct_prediction = tf.equal(
                tf.argmax(caches[caches['ZL']]), 
                tf.argmax(Y))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, 'float'))
        
        print ('Train Accuracy:', accuracy.eval({X: X_train.T,
                                                 Y: Y_train.T}))
        print ('Dev Accuracy:', accuracy.eval({X: X_dev.T,
                                                Y: Y_dev.T}))
    
        return parameters

def predict(X_data, parameters):
    (m, n_x) = X_data.shape
    X = tf.placeholder(tf.float32, shape = (n_x, None), name = 'X')
    caches = forward_prop(X, parameters)
    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        sess.run(init)
        z = sess.run(caches[caches['ZL']], feed_dict={X: X_data.T})
    return z.T
                       
# Main
parameters = build_neural_model(X_train, y_train, X_dev, y_dev, 
                                [10, 10, 10], 
                                num_epochs = 200,
                                print_cost = True)

y_pred = predict(X_test, parameters)

plt.plot(list(X_test), list(y_test), 'ro')
plt.plot(list(X_test), list(y_pred), 'bo')
plt.xlabel('input')
plt.ylabel('func')
plt.title('Test data')
plt.show()

#print(predict(X.T, parameters))