import math
import numpy as np
import h5py
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.python.framework import ops

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # ignoring warnings



def normalizer(x):
    m = x.shape[0]
    x = x - np.mean(x)
    x = (x * m) / (np.sum(x ** 2))
    return x

def ReLu(x):
    return np.maximum(0, x)

def sigmoid(z):
    x = tf.placeholder(tf.float32, name = 'x')
    results = tf.sigmoid(x)
    with tf.Session() as session:
        results = session.run(results, feed_dict={x: z})
    
    return results


def random_mini_batches(X, Y, mini_batch_size = 64, seed = 0):
    """
    Creates a list of random minibatches from (X, Y)
    
    Arguments:
    X of shape (input size, m)
    Y of shape (1, m)
    Returns:
    mini_batches -- list of synchronous (mini_batch_X, mini_batch_Y)
    """
    
    m = X.shape[1]                
    mini_batches = []
    np.random.seed(seed)
    
    # Shuffle (X, Y)
    permutation = list(np.random.permutation(m))
    shuffled_X = X[:, permutation]
    shuffled_Y = Y[:, permutation].reshape((Y.shape[0],m))

    # Partition (shuffled_X, shuffled_Y). Minus the end case.
    num_complete_minibatches = math.floor(m/mini_batch_size) # number of mini batches of size mini_batch_size in your partitionning
    for k in range(0, num_complete_minibatches):
        mini_batch_X = shuffled_X[:, k * mini_batch_size : k * mini_batch_size + mini_batch_size]
        mini_batch_Y = shuffled_Y[:, k * mini_batch_size : k * mini_batch_size + mini_batch_size]
        mini_batch = (mini_batch_X, mini_batch_Y)
        mini_batches.append(mini_batch)
    
    # Handling the end case (last mini-batch < mini_batch_size)
    if m % mini_batch_size != 0:
        mini_batch_X = shuffled_X[:, num_complete_minibatches * mini_batch_size : m]
        mini_batch_Y = shuffled_Y[:, num_complete_minibatches * mini_batch_size : m]
        mini_batch = (mini_batch_X, mini_batch_Y)
        mini_batches.append(mini_batch)
    
    return mini_batches




def trainFunction(X_train, Y_train, learning_rate = 0.0001,
          num_epochs = 1500, minibatch_size = 32, print_cost = True):

    ops.reset_default_graph()                         # to be able to rerun the model without overwriting tf variables
    tf.set_random_seed(1)                             # to keep consistent results
    seed = 3                    
    
    m = Y_train.shape[1]
    n_x = X_train.shape[0]
    n_y = Y_train.shape[0]

    X = tf.placeholder(shape=[n_x, None] ,dtype=tf.float32, name='X')
    Y = tf.placeholder(shape=[n_y, None] ,dtype=tf.float32, name='Y')
    
    costs = [] 

    # parameters = initialize_parameters()
    tf.set_random_seed(1)
    b1 = tf.get_variable("b1", [1, 1], initializer = tf.zeros_initializer())
    # using Xavier Initialization for weights
    W1 = tf.get_variable("W1", [1, n_x], initializer = tf.contrib.layers.xavier_initializer(seed = 1))

    Z1 = tf.add(tf.matmul(W1, X) , b1)

    cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits = Z1,  labels = Y))


    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)
    # optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(cost)
    
    init = tf.global_variables_initializer() # Initialize all the variables

    with tf.Session() as session:
        session.run(init)
        for i in range(num_epochs):
            seed = seed + 1
            epoch_cost = 0.
            minibatches = random_mini_batches(X_train, Y_train, minibatch_size, seed)
            n_minibatches = np.floor(m / minibatch_size)
            for minibatch in minibatches:
                (minibatch_X, minibatch_Y) = minibatch
                _ , minibatch_cost = session.run([optimizer, cost], feed_dict={X: minibatch_X, Y: minibatch_Y})
                epoch_cost += minibatch_cost / n_minibatches
                # epoch_cost += minibatch_cost / minibatch_cost.shape[1]

            
            if print_cost == True:
                if i % 100 == 0:
                    print ("Cost after epoch %i: %f" % (i, epoch_cost))
                if i % 5 == 0:
                    costs.append(epoch_cost)
            
        
        # plot the cost
        if print_cost == True:
            plt.plot(np.squeeze(costs))
            plt.ylabel('cost')
            plt.xlabel('iterations (per tens)')
            plt.title("Learning rate =" + str(learning_rate))
            plt.show()


        parameters = {
            "W1": W1,
            "b1": b1
        }
        parameters = session.run(parameters)

        print ("Parameters have been trained!")
        correct_prediction = tf.equal(tf.argmax(Z1), tf.argmax(Y))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
        print ("Train Accuracy:", accuracy.eval({X: X_train, Y: Y_train}))
        # print ("Test Accuracy:", accuracy.eval({X: X_test, Y: Y_test}))

    return parameters



def trainFunction2(X_train, Y_train, learning_rate = 0.0001,
          num_epochs = 1500, minibatch_size = 32, print_cost = True):

    ops.reset_default_graph()                         # to be able to rerun the model without overwriting tf variables
    tf.set_random_seed(1)                             # to keep consistent results
    seed = 3                    
    
    m = Y_train.shape[1]
    n_x = X_train.shape[0]
    n_y = Y_train.shape[0]

    X = tf.placeholder(shape=[n_x, None] ,dtype=tf.float32, name='X')
    Y = tf.placeholder(shape=[n_y, None] ,dtype=tf.float32, name='Y')
    
    costs = [] 

    # parameters = initialize_parameters()
    tf.set_random_seed(1)

    n1 = 32
    n2 = 32
    n3 = 16
    b1 = tf.get_variable("b1", [n1, 1], initializer = tf.zeros_initializer())
    b2 = tf.get_variable("b2", [n2, 1], initializer = tf.zeros_initializer())
    b3 = tf.get_variable("b3", [n3, 1], initializer = tf.zeros_initializer())
    b4 = tf.get_variable("b4", [1, 1], initializer = tf.zeros_initializer())
    # using Xavier Initialization for weights
    W1 = tf.get_variable("W1", [n1, n_x], initializer = tf.contrib.layers.xavier_initializer(seed = 1))
    W2 = tf.get_variable("W2", [n2, n1], initializer = tf.contrib.layers.xavier_initializer(seed = 1))
    W3 = tf.get_variable("W3", [n3, n2], initializer = tf.contrib.layers.xavier_initializer(seed = 1))
    W4 = tf.get_variable("W4", [1, n3], initializer = tf.contrib.layers.xavier_initializer(seed = 1))


    # Z3 = forward_propagation(X, parameters)
    Z1 = tf.add(tf.matmul(W1, X) , b1)
    A1 = tf.nn.relu(Z1)             
    Z2 = tf.add(tf.matmul(W2, A1) , b2)
    A2 = tf.nn.relu(Z2)   
    Z3 = tf.add(tf.matmul(W3, A2) , b3)
    A3 = tf.nn.relu(Z3)   
    Z4 = tf.add(tf.matmul(W4, A3) , b4)

    cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits = Z4,  labels = Y))


    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)
    # optimizer2 = tf.train.AdamOptimizer(learning_rate=learning_rate / 80).minimize(cost)
    # optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(cost)
    
    init = tf.global_variables_initializer() # Initialize all the variables

    with tf.Session() as session:
        session.run(init)
        for i in range(num_epochs):
            seed = seed + 1
            epoch_cost = 0.
            minibatches = random_mini_batches(X_train, Y_train, minibatch_size, seed)
            n_minibatches = np.floor(m / minibatch_size)
            for minibatch in minibatches:
                (minibatch_X, minibatch_Y) = minibatch
                _ , minibatch_cost = session.run([optimizer, cost], feed_dict={X: minibatch_X, Y: minibatch_Y})
                epoch_cost += minibatch_cost / n_minibatches
                # epoch_cost += minibatch_cost / minibatch_cost.shape[1]

                if print_cost == True:
                    if i % 100 == 0:
                        print ("Cost after epoch %i: %f" % (i, epoch_cost))
                    if i % 5 == 0:
                        costs.append(epoch_cost)
      
            
        
        # plot the cost
        if print_cost == True:
            plt.plot(np.squeeze(costs))
            plt.ylabel('cost')
            plt.xlabel('iterations (per tens)')
            plt.title("Learning rate =" + str(learning_rate))
            plt.show()


        parameters = {
            "W1": W1,
            "b1": b1,
            "W2": W2,
            "b2": b2,
            "W3": W3,
            "b3": b3,
            "W4": W4,
            "b4": b4
        }
        parameters = session.run(parameters)

        print ("Parameters have been trained!")
        correct_prediction = tf.equal(tf.argmax(Z1), tf.argmax(Y))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
        print ("Train Accuracy:", accuracy.eval({X: X_train, Y: Y_train}))
        # print ("Test Accuracy:", accuracy.eval({X: X_test, Y: Y_test}))

    return parameters






import pandas as pd
data = pd.read_csv("./datasets/train.csv")
# data = data[0:864]
# print(data.shape)
# print(data.head())
m = data.shape[0] #891
y = np.array([data.loc[:,'Survived']])

x1 = np.array(data.loc[:,'Pclass'])
x2 = np.array(data.loc[:,'Sex'])
x3 = np.array(data.loc[:,'Age'])  # has NAN
x4 = np.array(data.loc[:,'SibSp'])
x5 = np.array(data.loc[:,'Parch'])
x6 = np.array(data.loc[:,'Fare'])

x7 = np.array(data.loc[:,'Name'])
x8 = np.array(data.loc[:,'Embarked'])  # has NAN


x1 = normalizer(x1)
x4 = normalizer(x4)
x5 = normalizer(x5)
x6 = normalizer(x6)

x2[x2 == 'male'] = 1
x2[x2 == 'female'] = -1
x2 = normalizer(x2)

#solving unknown age problem
#replacing NANs with mean of ages
f = np.isnan(x3)
cnt = 0
for i in f:
    if i == True:
        cnt += 1
x3 = np.nan_to_num(x3)
mean = np.sum(x3) / (m - cnt)
x3[x3 == 0] = mean
x3 = normalizer(x3)





x8[x8 == 'S'] = 1
x8[x8 == 'C'] = 2
x8[x8 == 'Q'] = 3

f = pd.isnull(x8)
c = []
for i in range(len(f)) :
    if f[i] == True:
        c.append(i)
for i in c:
    x8[i] = 0
mean = np.sum(x8) / (m - len(c))
x8[x8 == 0] = mean
x8 = normalizer(x8)





for i in range(len(x7)):
    if "Mr." in x7[i]:
        x7[i] = 1
    elif "Mrs." in x7[i]:
        x7[i] = 2
    elif "Miss." in x7[i]:
        x7[i] = 3
    elif "Master." in x7[i]:
        x7[i] = 4
    elif "Dr." in x7[i]:
        x7[i] = 5
    else :
        # print(x7[i])
        x7[i] = 6

x7 = normalizer(x7)

#x7 = Name{
# Mr.
# Mrs.
# Miss.
# Master.
# Dr.
# Lady. (Lucille Christiana Sutherland) ("Mrs Morgan")    #1
# Ms. Encarnacion                                         #1
# Sir. Cosmo Edmund ("Mr Morgan")                         #1
# Don.                                                    #1
# Rev.                                                    #6
# Mme.                                                    #1
# Ms.                                                     #1
# Major.                                                  #2
# Gordon.                                                 #2
# Mlle.                                                   #2
# Col.                                                    #2
# Capt.                                                   #1
# Countess.                                               #1
# Jonkheer.                                               #1
# }


x = np.vstack((x1, x2, x3, x4, x5, x6))
# x = np.vstack((x1, x2, x3, x4, x5, x6, x7, x8))
# print(x.shape)


X_train = x
Y_train = y
m = Y_train.shape[1]
# print(X_train.shape)
# print(Y_train.shape)


# data = pd.read_csv("./datasets/test.csv")
# print(data.shape)


# TODO TODO TODO TODO TODO TODO TODO RUN MODEL HERE TODO TODO TODO TODO TODO TODO TODO TODO TODO
parameters = trainFunction2(X_train, Y_train, 0.008, 10000, m, True)


def pred(parameters, X, Y_train):

    W1 = parameters['W1']
    b1 = parameters['b1']


    Y = np.dot(W1, X) + b1
    Y = sigmoid(Y)[0]
    Y = np.around(Y)
    Y_train = Y_train[0]
    Y_train = Y_train.astype(int)
    # print(Y[0:5])
    # print(Y_train[0:5])

    g = np.subtract(Y, Y_train)
    g = abs(g)
    print(np.sum(g))
    print("Train Accuracy = " + str(1 - (np.sum(g)) / m))
    # print(parameters['W1'])
    # print(parameters['b1'])




def pred2(parameters, X, Y_train):

    W1 = parameters['W1']
    b1 = parameters['b1']
    W2 = parameters['W2']
    b2 = parameters['b2']
    W3 = parameters['W3']
    b3 = parameters['b3']
    W4 = parameters['W4']
    b4 = parameters['b4']

    Z1 = np.dot(W1, X) + b1
    A1 = ReLu(Z1)         
    Z2 = np.dot(W2, A1) + b2
    A2 = ReLu(Z2) 
    Z3 = np.dot(W3, A2) + b3
    A3 = ReLu(Z3) 
    Z4 = np.dot(W4, A3) + b4
    Y = sigmoid(Z4)[0]
    Y = np.around(Y)
    Y_train = Y_train[0]
    Y_train = Y_train.astype(int)
    # print(Y[0:5])
    # print(Y_train[0:5])

    g = np.subtract(Y, Y_train)
    g = abs(g)
    print(np.sum(g))
    print("Train Accuracy = " + str(1 - (np.sum(g)) / m))


# TODO TODO TODO TODO TODO TODO TODO PREDICT MODEL HERE TODO TODO TODO TODO TODO TODO TODO TODO TODO
pred2(parameters, x, Y_train)



""" Results :
8 features
m 0.05 1000
80%

6 features
79%

4layer
n_x = 8
83%

4layer
n_x = 8
learning rate = 0.008
90%
"""