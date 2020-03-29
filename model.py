import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

# #trying the Decision tree

# data = pd.read_csv('tracks.csv')

# Y = data['Label']

# data = data.drop('Label', axis=1)

# X = data

# X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.25, random_state=0, stratify=Y)

# clf = DecisionTreeClassifier()
# clf = clf.fit(X_train, y_train)

# print(clf.predict(X_test.iloc[0:10]))
# print(clf.score(X_test,y_test))

import pickle

# filename = 'tree.pkl'
# decision_tree_model_pkl = open(filename, 'wb')
# pickle.dump(clf, decision_tree_model_pkl)
# decision_tree_model_pkl.close()
# s = pickle.dumps(clf)


import tensorflow as tf

data = pd.read_csv('tracks.csv')

labels = data['Label']

data = data.drop('Label', axis=1)

train, test, training_label, test_label = train_test_split(data, labels, test_size=0.20, random_state=0, stratify=labels)


def input_fn(features, labels, training=True, batch_size=256):
    #Create dataset
    dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))

    if training:
        dataset = dataset.shuffle(1000).repeat()
    return dataset.batch(batch_size)

feat_cols = []


for k in train.keys():
    feat_cols.append(tf.feature_column.numeric_column(key=k))

#instantiate the classifier

classifier = tf.estimator.DNNClassifier(hidden_units=[1024, 512, 256], feature_columns= feat_cols, n_classes=3)

classifier.train(input_fn=lambda: input_fn(train,training_label, training=True), steps= 5000)


eval_result = classifier.evaluate(input_fn = lambda: input_fn(test,test_label, training=False))
print('\n Test accuracy : {accuracy:0.3f}\n'.format(**eval_result))