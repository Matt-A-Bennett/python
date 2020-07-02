import numpy as np

def make_bars(n_images, n_locations, orientation):
    images = []
    for location in n_locations:
        for i in n_images:
            image = np.zeros((7,7))
            if orientation == "vertical":
                image[:,location] = 1
            elif orientation == "horizontal":
                image[location,:] = 1
            images.append(image)
    return images

class Neuron():
    def __init__(self, synaptic_weights, rf_location=(0,0), rf_size=1):
        self.synaptic_weights = synaptic_weights
        self.rf_location = rf_location
        self.rf_size = rf_size

    # The Sigmoid function, which describes an S shaped curve.
    # We pass the weighted sum of the inputs through this function to
    # normalise them between 0 and 1.
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    # The derivative of the Sigmoid function.
    # This is the gradient of the Sigmoid curve.
    # It indicates how confident we are about the existing weight.
    def sigmoid_derivative(self, x):
        return x * (1 - x)

    # The neuron thinks.
    def think(self, inputs):
        # Pass inputs through our neuron
        return self.sigmoid(np.dot(inputs, self.synaptic_weights))

    # We train the neuron through a process of trial and error.
    # Adjusting the synaptic weights each time.
    def train(self, training_set_inputs, training_set_outputs, number_of_training_iterations):
        for iteration in range(number_of_training_iterations):
            # Pass the training set through our neuron
            output = self.think(training_set_inputs)

            # Calculate the error (The difference between the desired output
            # and the predicted output).
            error = training_set_outputs - output

            # Multiply the error by the input and again by the gradient of the Sigmoid curve.
            # This means less confident weights are adjusted more.
            # This means inputs, which are zero, do not cause changes to the weights.
            adjustment = np.dot(training_set_inputs.T, error * self.sigmoid_derivative(output))

            # Adjust the weights.
            self.synaptic_weights += adjustment

# Create binary images containing horizontal or vertical bars to train on
n_images = range(1,6)
n_locations = range(1,6)
vertical = make_bars(n_images, n_locations, orientation="vertical")
horizontal = make_bars(n_images, n_locations, orientation="horizontal")
images = vertical + horizontal

# Vectorise images
vector_images = []
for image in images:
    vector_images.append(image.ravel().T)
# vector_images =

# Seed the np.random number generator, so it generates the same numbers
# every time the program runs.
# np.random.seed(1)

# We model a single neuron, with 3 input connections and 1 output connection.
# We assign np.random weights to a 3 x 1 matrix, with values in the range -1 to 1
# and mean 0.
synaptic_weights = 2 * np.random.random((7, 7)) - 1
# print(synaptic_weights)
synaptic_weights = synaptic_weights.ravel()
# print(synaptic_weights)

#Intialise a single neuron neuron.
neural_network = Neuron(synaptic_weights)

# print("np.random starting synaptic weights: ")
# print(neural_network.synaptic_weights)

# training_set_inputs = np.array([[0, 0, 1], [1, 1, 1], [1, 0, 1], [0, 1, 1]])
vertical_labels = np.ones((7,1))
horizonta_labels = np.zeros((7,1))
training_set_outputs = np.concatenate([vertical_labels, horizonta_labels])
# print(training_set_outputs)
# training_set_outputs = np.array([[1, 1, 1, 0]]).T
# print(training_set_outputs)

# Train the neuron using a training set.
# Do it 10,000 times and make small adjustments each time.
# neural_network.train(vector_images, training_set_outputs, 10000)

# print("New synaptic weights after training: ")
# print(neural_network.synaptic_weights)

# Test the neuron with a new situation.
# print("Considering new situation [1, 0, 0] -> ?: ")
# print(neural_network.think(np.array([1, 0, 0])))
