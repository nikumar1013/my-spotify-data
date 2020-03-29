import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

#trying the Decision tree

data = pd.read_csv('tracks.csv')

Y = data['Label']

data = data.drop('Label', axis=1)

X = data

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.25, random_state=0, stratify=Y)

clf = DecisionTreeClassifier()
clf = clf.fit(X_train, y_train)

print(clf.predict(X_test.iloc[0:10]))
print(clf.score(X_test,y_test))

import pickle

filename = 'tree.pkl'
decision_tree_model_pkl = open(filename, 'wb')
pickle.dump(clf, decision_tree_model_pkl)
decision_tree_model_pkl.close()
s = pickle.dumps(clf)


import tensorflow as tf