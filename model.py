import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pickle
from numpy import loadtxt
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
#trying the Decision tree

data = pd.read_csv('tracks.csv')

Y = data['Label']

data = data.drop('Label', axis=1)

X = data

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.30, random_state=0, stratify=Y)

clf = DecisionTreeClassifier()
clf = clf.fit(X_train, y_train)

print(clf.predict(X_test.iloc[0:10]))
print("Decision tree classifier score : {}", clf.score(X_test,y_test))

xgb = XGBClassifier()
xgb.fit(X_train, y_train)

print("XGBoost classifier score : {}", xgb.score(X_test,y_test))

log = LogisticRegression(random_state=0).fit(X_train, y_train)

print("LogisticRegression classifier score : {}", log.score(X_test,y_test))

forest = RandomForestClassifier(max_depth=2, random_state=0)
forest.fit(X_train, y_train)

print("RandomForestClassifier classifier score : {}", forest.score(X_test,y_test))
filename = 'xgb.pkl'
model_pkl = open(filename, 'wb')
pickle.dump(xgb, model_pkl)
model_pkl.close()
s = pickle.dumps(xgb)


# import tensorflow as tf

# data = pd.read_csv('tracks.csv')

# labels = data['Label']

# data = data.drop('Label', axis=1)

# train, test, training_label, test_label = train_test_split(data, labels, test_size=0.20, random_state=0, stratify=labels)


# def input_fn(features, labels, training=True, batch_size=256):
#     #Create dataset
#     dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))

#     if training:
#         dataset = dataset.shuffle(1000).repeat()
#     return dataset.batch(batch_size)

# feat_cols = []


# for k in train.keys():
#     feat_cols.append(tf.feature_column.numeric_column(key=k))

# #instantiate the classifier
# classifier = tf.estimator.DNNClassifier(hidden_units=[30, 10], optimizer = 'Adagrad', feature_columns= feat_cols, n_classes=3)

# classifier.train(input_fn=lambda: input_fn(train,training_label, training=True), steps= 5000)


# eval_result = classifier.evaluate(input_fn = lambda: input_fn(test,test_label, training=False))
# print('\n Test accuracy : {accuracy:0.3f}\n'.format(**eval_result))

# def input_fn_2(features,batch_size=256):
# 	return tf.data.Dataset.from_tensor_slices(dict(features)).batch(batch_size)

# independant  = test
# predictions = classifier.predict(input_fn=lambda: input_fn_2(independant))
# SPECIES = ['0', '1', '2']
# real = []
# pred = []
# for pred_dict, expec in zip(predictions, test_label):
#     class_id = pred_dict['class_ids'][0]
#     probability = pred_dict['probabilities'][class_id]
#     pred.append(SPECIES[class_id])
#     real.append(expec)
#     print('Prediction is "{}" ({:.1f}%), expected "{}"'.format(
#         SPECIES[class_id], 100 * probability, expec))


# x_ax = range(0,len(real))   
# plt.plot(x_ax, real, 'r--', x_ax,pred, 'bs')
# plt.show()
