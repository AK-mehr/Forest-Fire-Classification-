# -*- coding: utf-8 -*-
"""Forest_fire.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fbEFcUaxJmLhMsNyG4gC35xYXBXTVC5x

##Preprocessing phase
"""

# !pip install opencv-python
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import gdown
import zipfile

url_fire_dataset = 'https://drive.google.com/u/0/uc?id=1XTDlTqZbjwwbhSDcA86LqrjuKmCcanfs&export=download'
base_path = ''

def download_from_drive():
  zip_path = base_path + 'fire_dataset.zip'
  extract_path = base_path
  img_folder = base_path + 'fire_dataset'

  if os.path.exists(img_folder) == False:
    if os.path.isfile(zip_path) == False:
      gdown.download(url_fire_dataset, zip_path, quiet=False, fuzzy=True)
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(path=extract_path)
    zip_ref.close()

download_from_drive()

def load_dataset(dataset_path):
  image_paths = list(paths.list_images(dataset_path))
  data = []

  for img in image_paths:
    image = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (128, 128))
    data.append(image)

  return np.array(data, dtype='float32')

# from pyimagesearch import config
from imutils import paths
import argparse
import sys
import random

fire_path = '/content/fire_dataset/fire_images'
non_fire_path = '/content/fire_dataset/non_fire_images'

fire_list = os.listdir(fire_path)
non_fire_list = os.listdir(non_fire_path)
classes = ['Fire', 'Non_Fire']

# total_list = fire_list + non_fire_list
# random.shuffle(total_list)

# images = cv2.imread(total_list)

fire_data = load_dataset(fire_path)
non_fire_data = load_dataset(non_fire_path)

# construct the class labels for the data
fireLabels = np.ones((fire_data.shape[0],))
nonFireLabels = np.zeros((non_fire_data.shape[0],))
# stack the fire data with the non-fire data, then scale the data
# to the range [0, 1]
data = np.vstack([fire_data, non_fire_data])
labels = np.hstack([fireLabels, nonFireLabels])
data /= 255

"""##Training phase"""

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score

X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=1, shuffle=True)

number_of_train = X_train.shape[0]
number_of_test = X_test.shape[0]

X_train_flatten = X_train.reshape(number_of_train,X_train.shape[1]*X_train.shape[2])
X_test_flatten = X_test .reshape(number_of_test,X_test.shape[1]*X_test.shape[2])
print("X train flatten",X_train_flatten.shape)
print("X test flatten",X_test_flatten.shape)


X_train = X_train_flatten.T
X_test = X_test_flatten.T
y_train = y_train.T
y_test = y_test.T
print("x train: ",X_train.shape)
print("x test: ",X_test.shape)
print("y train: ",y_train.shape)
print("y test: ",y_test.shape)

def initialize_weights_and_bias(dimension):
    w = np.full((dimension,1),0.01)
    b = 0.0
    return w, b

def sigmoid(z):
    y_head = 1/(1+np.exp(-z))
    return y_head

def forward_backward_propagation(w,b,x_train,y_train):
    # forward propagation
    z = np.dot(w.T,x_train) + b
    y_head = sigmoid(z)
    loss = -y_train*np.log(y_head)-(1-y_train)*np.log(1-y_head)
    cost = (np.sum(loss))/x_train.shape[1]
    # backward propagation
    derivative_weight = (np.dot(x_train,((y_head-y_train).T)))/x_train.shape[1]
    derivative_bias = np.sum(y_head-y_train)/x_train.shape[1]
    gradients = {"derivative_weight": derivative_weight,"derivative_bias": derivative_bias}
    return cost,gradients

def update(w, b, x_train, y_train, learning_rate,number_of_iterarion):
    cost_list = []
    cost_list2 = []
    index = []
    
    for i in range(number_of_iterarion):
        
        cost,gradients = forward_backward_propagation(w,b,x_train,y_train)
        cost_list.append(cost)
        
        w = w - learning_rate * gradients["derivative_weight"]
        b = b - learning_rate * gradients["derivative_bias"]
        if i % 100 == 0:
            cost_list2.append(cost)
            index.append(i)
            print ("Cost after iteration %i: %f" %(i, cost))
    
    parameters = {"weight": w,"bias": b}
    plt.plot(index,cost_list2)
    plt.xticks(index,rotation='vertical')
    plt.xlabel("Number of Iterarion")
    plt.ylabel("Cost")
    plt.show()
    return parameters, gradients, cost_list

def predict(w,b,x_test):
    
    z = sigmoid(np.dot(w.T,x_test)+b)
    Y_prediction = np.zeros((1,x_test.shape[1]))

    for i in range(z.shape[1]):
        if z[0,i]<= 0.5:
            Y_prediction[0,i] = 0
        else:
            Y_prediction[0,i] = 1

    return Y_prediction

def logistic_regression(x_train, y_train, x_test, y_test, learning_rate ,  num_iterations):

    dimension =  x_train.shape[0]
    w,b = initialize_weights_and_bias(dimension)

    parameters, gradients, cost_list = update(w, b, x_train, y_train, learning_rate,num_iterations)
    
    y_prediction_test = predict(parameters["weight"],parameters["bias"],x_test)
    y_prediction_train = predict(parameters["weight"],parameters["bias"],x_train)
    
    print("Test Accuracy: {} %".format(round(100 - np.mean(np.abs(y_prediction_test - y_test)) * 100,2)))
    print("Train Accuracy: {} %".format(round(100 - np.mean(np.abs(y_prediction_train - y_train)) * 100,2)))

logistic_regression(X_train, y_train, X_test, y_test,learning_rate = 0.01, num_iterations = 1500)

clf =LogisticRegression(random_state=42)
clf.fit(X_train.T,y_train.T)

predictions = clf.predict(X_test.T)
cm = confusion_matrix(y_test, predictions, labels=clf.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=clf.classes_)
disp.plot()
plt.show()

grid={"C":np.logspace(-3,3,7),"penalty":["l1","l2"]}
log_reg_cv=GridSearchCV(clf,grid,cv=2, n_jobs=2)
log_reg_cv.fit(X_train.T,y_train.T)

print("best hyperparameters: ", log_reg_cv.best_params_)
print("accuracy: ", log_reg_cv.best_score_)

log_reg= LogisticRegression(C=0.001, penalty='l2', solver='liblinear')
log_reg.fit(X_train.T,y_train.T)
print("test accuracy: {} ".format(log_reg.fit(X_test.T, y_test.T).score(X_test.T, y_test.T)))
print("train accuracy: {} ".format(log_reg.fit(X_train.T, y_train.T).score(X_train.T, y_train.T)))

y_predict_prob = clf.predict_proba(X_test.T)
y_predict_prob_fire = y_predict_prob[:, 1]

y_predict_class_1 = [1 if prob > 0.4 else 0 for prob in y_predict_prob_fire]
print("Accuracy:", round(accuracy_score(y_test.T, y_predict_class_1), 3))

y_predict_class_2 = [1 if prob > 0.6 else 0 for prob in y_predict_prob_fire]
print("Accuracy:", round(accuracy_score(y_test.T, y_predict_class_2), 3))

import pickle

filename = 'classifier.py'
pickle.dump(log_reg, open(filename, 'wb'))
optimal_model = pickle.load(open(filename, 'rb'))
result = optimal_model.score(X_test.T, y_test.T)
print(result)

link = 'https://drive.google.com/u/0/uc?id=1z5zo5XwicHd7K471musPjn14hnbZIL7r&export=download'
zip_path = base_path + 'test_data.zip'

gdown.download(link,zip_path, quiet=False, fuzzy=True)
zip_ref = zipfile.ZipFile(zip_path, 'r')
zip_ref.extractall(path='')
zip_ref.close()

directory = '/content/download_data'

test_data = load_dataset(directory)
number_of_test = test_data.shape[0]

test_data_flatten = test_data.reshape(number_of_test,test_data.shape[1]*test_data.shape[2])
print("test flatten",test_data_flatten.shape)

test_data = test_data_flatten.T
print("test: ",test_data.shape)

path = '/content/download_data/'
new_path = ''
filename = os.listdir(path)
font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
thickness = 2

for (i, num) in enumerate(test_data.T):
  label = optimal_model.predict(np.expand_dims(num, axis=0))
  text = 'Fire' if label == 1 else 'non_Fire'
  img_path = os.path.join(path, filename[i])
  image = cv2.imread(img_path)
  image = cv2.resize(image, (128, 128))
  # output = image.copy()
  color = (255, 0, 0) if label == 1 else (0, 255, 0)
  image = cv2.putText(image, text, org, font, fontScale, color, thickness, cv2.LINE_AA)
  # dir = 'labelled images'
  # os.mkdir(dir)
  cv2.imwrite(f'img_{i}.png' ,image)


cv2.waitKey(0)
cv2.destroyAllWindows()

fig, ax = plt.subplots(1, 4, figsize=(10, 3))

for i in range(4): 
  img = cv2.imread(f'img_{i}.png')
  ax[i].imshow(img)
  ax[i].grid(False)
  ax[i].axis('off')

