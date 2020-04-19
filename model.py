# Author: Abhijit Raman
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

data = pd.read_csv('ml/tracks.csv')

Y = data['Label']

data = data.drop('Label', axis=1)

X = data

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.20, random_state=0, stratify=Y)


clf = DecisionTreeClassifier(random_state=0, max_depth=15)
clf.fit(X_train, y_train)
print("DecisionTree Classifier  score : {}", clf.score(X_test,y_test))

filename = 'ml/dtc.pkl'
model_pkl = open(filename, 'wb')
pickle.dump(clf, model_pkl)
model_pkl.close()
s = pickle.dumps(clf)