import pandas as pd
import numpy as np
from sklearn import preprocessing, neighbors
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib import style

# Using breast cancer data from:
# https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/

#   #  Attribute                     Domain
#   -- -----------------------------------------
#   1. Sample code number            id number
#   2. Clump Thickness               1 - 10
#   3. Uniformity of Cell Size       1 - 10
#   4. Uniformity of Cell Shape      1 - 10
#   5. Marginal Adhesion             1 - 10
#   6. Single Epithelial Cell Size   1 - 10
#   7. Bare Nuclei                   1 - 10
#   8. Bland Chromatin               1 - 10
#   9. Normal Nucleoli               1 - 10
#  10. Mitoses                       1 - 10
#  11. Class:                        (2 for benign, 4 for malignant)

df = pd.read_csv("breast-cancer-wisconsin.data")
df.replace("?", -99999, inplace=True)
df.drop(["id"], 1, inplace=True)

X = np.array(df.drop(["class"], 1))
y = np.array(df["class"])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
clf = neighbors.KNeighborsClassifier()
clf.fit(X_train, y_train)

accuracy = clf.score(X_test, y_test)
print(f"KNeighborsClassifier accuracy: {accuracy}")

example_measures = np.array([[4,2,1,1,1,2,3,2,1],
                             [4,2,1,2,2,2,3,2,1]])
example_measures = example_measures.reshape(len(example_measures),-1)
prediction = clf.predict(example_measures)
print(f"Predict Examples: {prediction}")

