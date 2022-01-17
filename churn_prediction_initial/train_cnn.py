import cv2
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.optimizers import *
from tensorflow.keras.utils import *
from tensorflow.python.keras import datasets, layers, models
from tensorflow.python.keras.layers import Conv2D,MaxPooling2D,Dense,Flatten,Dropout
from tensorflow.python.keras.callbacks import EarlyStopping
from churn_prediction_initial.new_metrics import *
import random


def getRandomIndex(num,ran):
    list = random.sample(range(0,ran),num)
    return list


def main():
    batch_size = 64
    epoch = 50

    churn_num = 348
    loyal_num = 16
    train_churn_num = 239
    train_loyal_num = 11
    train_num = train_churn_num + train_loyal_num

    train_labels = np.zeros((train_num,2))
    train_images = np.zeros((train_num,12,9))
    train_churn_images = np.zeros((train_churn_num,12,9))
    train_loyal_images = np.zeros((train_loyal_num,12,9))

    churn_index_list = getRandomIndex(train_churn_num,churn_num)
    loyal_index_list = getRandomIndex(train_loyal_num,loyal_num)
    filenames = ['commits','issues','issue_comments','pulls','merged_pulls','reviews',
                 'review_comments','dcn_betweeness_normalized','dcn_weighted_degree']

    max_min_val=dict()
    with open('data/max_min_values.txt','r') as f:
        for line in f.readlines():
            list = line.strip('\n').split('\t')
            max_min_val.update({list[0]:[float(list[1]),float(list[2])]})

    for i in range(9):
        csvFile = pd.read_csv('data/churn_'+filenames[i]+'.csv')
        deno = max_min_val[filenames[i]][0]-max_min_val[filenames[i]][1]
        j=0
        for index in churn_index_list:
            for k in range(12):
                train_churn_images[j][k][i] = csvFile.loc[index][k+1]/deno
            j+=1

    for i in range(9):
        csvFile = pd.read_csv('data/loyal_'+filenames[i]+'.csv')
        deno = max_min_val[filenames[i]][0]-max_min_val[filenames[i]][1]
        j=0
        for index in loyal_index_list:
            for k in range(12):
                train_loyal_images[j][k][i] = csvFile.loc[index][k+1]/deno
            j+=1

    random_index_list = sorted(getRandomIndex(train_loyal_num,train_num))       #随机获取11个下标，用于随机插入忠诚用户数据
    p = 0
    q = 0
    churn_label = np.zeros(2)
    loyal_label = np.zeros(2)
    churn_label[0]=1
    loyal_label[1]=1
    for i in range(train_num):
        if i in random_index_list:
            train_images[i]=train_loyal_images[p]
            train_labels[i]=loyal_label
            p += 1
        else:
            train_images[i]=train_churn_images[q]
            train_labels[i]=churn_label
            q += 1

    train_images = train_images[..., np.newaxis]
    # print(train_images.shape)

    # model = models.Sequential()
    # model.add(Conv2D(input_shape=(12, 9, 1), filters=8, kernel_size=(4, 1),
    #                  strides=1, padding='same', name='conv1', #activation='relu',
    #                  kernel_initializer=keras.initializers.RandomUniform(minval=-0.354, maxval=0.354, seed=None),    #按随机分布初始化权重，区间为（-1/n^0.5,1/n^0.5)
    #                  kernel_regularizer=tf.keras.regularizers.l2(0.045)
    #                  ))
    # model.add(Conv2D(7,(1,4),strides=1,padding='same',activation='relu',name='conv2',
    #                  kernel_initializer=keras.initializers.RandomUniform(minval=-0.378, maxval=0.378, seed=None),
    #                  kernel_regularizer=tf.keras.regularizers.l2(0.045)))
    # model.add(MaxPooling2D(2, 2, 'same', name='maxpool'))   #最大池化层，池化核大小2*2
    # model.add(Flatten(name='flatten'))
    # model.add(Dense(120, activation='relu', name='fc1',
    #                 kernel_initializer=keras.initializers.RandomUniform(minval=-0.091, maxval=0.091, seed=None),
    #                 kernel_regularizer=tf.keras.regularizers.l2(0.045)))
    # model.add(Dense(120, activation='relu', name='fc2',
    #                 kernel_initializer=keras.initializers.RandomUniform(minval=-0.091, maxval=0.091, seed=None),
    #                 kernel_regularizer=tf.keras.regularizers.l2(0.045)))
    # model.add(Dropout(0.5))
    # model.add(Dense(2, activation='softmax', name='output_layer',
    #                 kernel_initializer=keras.initializers.RandomUniform(minval=-0.707, maxval=0.707, seed=None),
    #                 kernel_regularizer=tf.keras.regularizers.l2(0.045)))
    model = models.Sequential()
    # Block 1
    model.add(Conv2D(input_shape=(12, 9, 1), filters=64, kernel_size=3,
                     strides=1, padding='same', activation='relu', name='block1_conv1',
                     kernel_initializer='random_uniform',
                     kernel_regularizer=tf.keras.regularizers.l2(0.045)))
    model.add(Conv2D(64, 3, strides=1, padding='same', activation='relu', name='block1_conv2',
                     kernel_initializer='random_uniform'))
    model.add(MaxPooling2D(2, 2, 'same', name='block1_maxpool'))

    # Block 2
    model.add(Conv2D(128, 3, strides=1, padding='same', activation='relu', name='block2_conv1',
                     kernel_initializer='random_uniform'))
    model.add(Conv2D(128, 3, strides=1, padding='same', activation='relu', name='block2_conv2',
                     kernel_initializer='random_uniform'))
    model.add(MaxPooling2D(2, 2, 'same', name='block2_maxpool'))

    # Block 3
    model.add(Conv2D(256, 3, strides=1, padding='same', activation='relu', name='block3_conv1',
                     kernel_initializer='random_uniform'))
    model.add(Conv2D(256, 3, strides=1, padding='same', activation='relu', name='block3_conv2',
                     kernel_initializer='random_uniform'))
    model.add(Conv2D(256, 3, strides=2, padding='same', activation='relu', name='block3_conv3',
                     kernel_initializer='random_uniform'))
    model.add(MaxPooling2D(2, 2, 'same', name='block3_maxpool'))

    # Block 4
    model.add(Conv2D(512, 3, strides=1, padding='same', activation='relu', name='block4_conv1',
                     kernel_initializer='random_uniform'))
    model.add(Conv2D(512, 3, strides=1, padding='same', activation='relu', name='block4_conv2',
                     kernel_initializer='random_uniform'))
    model.add(Conv2D(512, 3, strides=1, padding='same', activation='relu', name='block4_conv3',
                     kernel_initializer='random_uniform'))
    model.add(MaxPooling2D(2, 2, 'same', name='block4_maxpool'))
    """
    # Block 5
    model.add(Conv2D(512,3,strides=1,padding='same',activation='relu',name='block5_conv1'))
    model.add(Conv2D(512,3,strides=1,padding='same',activation='relu',name='block5_conv2'))
    model.add(Conv2D(512,3,strides=1,padding='same',activation='relu',name='block5_conv3'))
    model.add(MaxPooling2D(2,2,'same',name='block5_maxpool'))
    """
    model.add(Flatten(name='flatten'))
    '''model.add(Dense(4096, activation='relu', name='fc_layer1',
                    kernel_initializer='random_uniform'))'''
    model.add(Dense(1024, activation='relu', name='fc_layer2',
                    kernel_initializer='random_uniform'))
    model.add(Dense(256, activation='relu', name='fc_layer3',
                    kernel_initializer='random_uniform'))
    model.add(Dropout(0.3))
    model.add(Dense(2, activation='softmax', name='predictions_layer',
                    kernel_initializer='random_uniform'))

    print("创建CNN完成 ...")
    model.summary()  # 显示模型的架构
    # compile model
    sgd = keras.optimizers.SGD(lr=0.1, momentum=0.9)
    model.compile(optimizer=sgd,
                  loss='categorical_crossentropy',
                  metrics=['categorical_accuracy',micro_precision,macro_precision,#micro_auroc,macro_auroc,
                           micro_recall,macro_recall,micro_f1_score,macro_f1_score])

    callbacks = [
        # Interrupt training if `val_loss` stops improving for over 3 epochs
        keras.callbacks.EarlyStopping(monitor='val_loss', mode='min', min_delta=0.00001, patience=5, verbose=1),
        # Write TensorBoard logs to `./logs` directory
        keras.callbacks.TensorBoard(log_dir='./logs')
    ]
    model.fit(x=train_images, y=train_labels, batch_size=64, epochs=50, shuffle=True, verbose=1, #callbacks=callbacks,
              validation_split=0.2)
    model.save('predict_model.h5')  # 保存为h5模型


if __name__ == '__main__':
    main()