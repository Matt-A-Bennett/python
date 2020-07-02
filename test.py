from scipy.io import loadmat

test = loadmat('/home/mattb/code/matlab/test_file.mat')
type(test)
test.keys()
ideco = test['ideco']
ideco.dtype
type(ideco)
ideco.shape
ideco = ideco[0,0]
ideco.dtype
ideco.shape

# select the 'run' field of the ideco structure
runs = ideco['run']

runs['run_name'] # array containing another array for each run holding the run name
runs['run_name'][0][0] # grab the first array from inside the outer array
runs['run_name'][0][0][0] # the string of the run name itself
runs['data'] # the data across all runs
runs['data'][0] # an array containing an array for each run's vtc data
run1_data = runs['data'][0][0] # this is the actual vtc data (for run1)!
run2_data = runs['data'][0][1] # this is the actual vtc data (for run2)!

# You should use -v7.3 while saving in Matlab as it uses a better/more supported/standardized format.
import numpy as np
import h5py
f = h5py.File('somefile.mat','r')
data = f.get('data/variable1')
data = np.array(data) # For converting to a NumPy array

