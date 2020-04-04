# Author: Abhijit Raman

import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
#trying the Decision tree

data = pd.read_csv('tracks.csv')

Y = data['Label']

data = data.drop('Label', axis=1)

X = data

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.30, random_state=0, stratify=Y)

xgb = XGBClassifier(
	learning_rate=0.15,
	n_estimators=1000,
	max_depth=6,
	min_child_weight=1,
	gamma=0,
	subsample=.8,
	colsample_bytree=.8,
	objective="binary:logistic",
	nthread=4
	)
xgb.fit(X_train, y_train)

print("XGBoost classifier score : {}", xgb.score(X_test,y_test))

filename = 'xgb.pkl'
model_pkl = open(filename, 'wb')
pickle.dump(xgb, model_pkl)
model_pkl.close()
s = pickle.dumps(xgb)