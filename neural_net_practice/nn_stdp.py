'''
Associated YT tutorial: https://youtu.be/TEWy9vZcxW4
'''

import numpy as np

np.random.seed(0)

X = [[1, 2, 3, 2.5],
     [2.0, 5.0, -1.0, 2.0],
     [-1.5, 2.7, 3.3, -0.8]]

class Layer_Dense:
    def __init__(self, n_inputs, n_neurons):
        self.weights = 0.10 * np.random.randn(n_inputs, n_neurons)
        self.biases = np.zeros((1, n_neurons))
    def forward(self, inputs):
        self.output = np.dot(inputs, self.weights) + self.biases

class Activation_ReLU:
    def forward(self, inputs):
        self.output = np.maximum(0, inputs)


# build network
layer1 = Layer_Dense(n_inputs=4, n_neurons=5)
activation1 = Activation_ReLU()
layer2 = Layer_Dense(5,2)

print("\ninputs:")
print(X)

# propagate network
layer1.forward(X)
print("\nlayer1 intial output")
print(layer1.output)
activation1.forward(layer1.output)
print("\nlayer1 activation output:")
print(activation1.output)
layer2.forward(activation1.output)
print("\nlayer2 intial output")
print(layer2.output)
