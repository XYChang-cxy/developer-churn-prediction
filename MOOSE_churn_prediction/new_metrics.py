import tensorflow as tf
from sklearn.metrics import roc_auc_score,precision_score,recall_score,f1_score
import numpy as np

# 此处的参数类型是numpy数组
def np_macro_auroc(y_true,y_pred):
    y_t = np.zeros(y_true.shape)
    y_p = np.zeros(y_pred.shape)
    flag = False
    for i in range(len(y_pred)):
        max_value = max(y_pred[i])
        for j in range(len(y_pred[i])):
            if max_value == y_pred[i][j] and flag == False:
                y_p[i][j] = 1
                flag = True
            else:
                y_p[i][j] = 0
            y_t[i][j] = y_true[i][j]
    return roc_auc_score(y_t, y_p,average='macro')


def macro_auroc(y_true,y_pred):
    # tf.py_func()接收的是tensor，然后将其转化为numpy array送入第一个参数中的函数，再将函数输出的numpy array转化为tensor返回。
    return tf.py_function(np_macro_auroc, (y_true, y_pred), tf.double)


# 此处的参数类型是numpy数组
def np_micro_auroc(y_true,y_pred):
    y_t = np.zeros(y_true.shape)
    y_p = np.zeros(y_pred.shape)
    flag = False
    for i in range(len(y_pred)):
        max_value = max(y_pred[i])
        for j in range(len(y_pred[i])):
            if max_value == y_pred[i][j] and flag == False:
                y_p[i][j] = 1
                flag = True
            else:
                y_p[i][j] = 0
            y_t[i][j] = y_true[i][j]
    return roc_auc_score(y_t,y_p,average='micro')


def micro_auroc(y_true,y_pred):
    # tf.py_func()接收的是tensor，然后将其转化为numpy array送入第一个参数中的函数，再将函数输出的numpy array转化为tensor返回。
    return tf.py_function(np_micro_auroc, (y_true, y_pred), tf.double)


# 此处的参数类型是numpy数组
def np_macro_precision(y_true,y_pred):
    y_t = np.zeros(y_true.shape)
    y_p = np.zeros(y_pred.shape)
    flag = False
    for i in range(len(y_pred)):
        max_value = max(y_pred[i])
        for j in range(len(y_pred[i])):
            if max_value == y_pred[i][j] and flag == False:
                y_p[i][j] = 1
                flag = True
            else:
                y_p[i][j] = 0
            y_t[i][j] = y_true[i][j]
    return precision_score(y_t, y_p,average='macro',zero_division=0)


def macro_precision(y_true,y_pred):
    return tf.py_function(np_macro_precision,(y_true,y_pred), tf.double)


def np_micro_precision(y_true,y_pred):
    y_t = np.zeros(y_true.shape)
    y_p = np.zeros(y_pred.shape)
    flag = False
    for i in range(len(y_pred)):
        max_value = max(y_pred[i])
        for j in range(len(y_pred[i])):
            if max_value == y_pred[i][j] and flag == False:
                y_p[i][j] = 1
                flag = True
            else:
                y_p[i][j] = 0
            y_t[i][j] = y_true[i][j]
    return precision_score(y_t, y_p,average='micro',zero_division=0)


def micro_precision(y_true,y_pred):
    return tf.py_function(np_micro_precision,(y_true,y_pred), tf.double)


def np_macro_recall(y_true,y_pred):
    y_t = np.zeros(y_true.shape)
    y_p = np.zeros(y_pred.shape)
    flag = False
    for i in range(len(y_pred)):
        max_value = max(y_pred[i])
        for j in range(len(y_pred[i])):
            if max_value == y_pred[i][j] and flag == False:
                y_p[i][j] = 1
                flag = True
            else:
                y_p[i][j] = 0
            y_t[i][j] = y_true[i][j]
    return recall_score(y_t, y_p,average='macro',zero_division=0)


def macro_recall(y_true,y_pred):
    return tf.py_function(np_macro_recall,(y_true,y_pred), tf.double)


def np_micro_recall(y_true,y_pred):
    y_t = np.zeros(y_true.shape)
    y_p = np.zeros(y_pred.shape)
    flag = False
    for i in range(len(y_pred)):
        max_value = max(y_pred[i])
        for j in range(len(y_pred[i])):
            if max_value == y_pred[i][j] and flag == False:
                y_p[i][j] = 1
                flag = True
            else:
                y_p[i][j] = 0
            y_t[i][j] = y_true[i][j]
    return recall_score(y_t, y_p,average='micro',zero_division=0)


def micro_recall(y_true,y_pred):
    return tf.py_function(np_micro_recall,(y_true,y_pred), tf.double)


def np_macro_f1(y_true,y_pred):
    y_t = np.zeros(y_true.shape)
    y_p = np.zeros(y_pred.shape)
    flag = False
    for i in range(len(y_pred)):
        max_value = max(y_pred[i])
        for j in range(len(y_pred[i])):
            if max_value == y_pred[i][j] and flag == False:
                y_p[i][j] = 1
                flag = True
            else:
                y_p[i][j] = 0
            y_t[i][j] = y_true[i][j]
    return f1_score(y_t, y_p,average='macro',zero_division=0)


def macro_f1_score(y_true,y_pred):
    return tf.py_function(np_macro_f1,(y_true,y_pred), tf.double)


def np_micro_f1(y_true,y_pred):
    y_t = np.zeros(y_true.shape)
    y_p = np.zeros(y_pred.shape)
    flag = False
    for i in range(len(y_pred)):
        max_value = max(y_pred[i])
        for j in range(len(y_pred[i])):
            if max_value == y_pred[i][j] and flag == False:
                y_p[i][j] = 1
                flag = True
            else:
                y_p[i][j] = 0
            y_t[i][j] = y_true[i][j]
    return f1_score(y_t, y_p,average='micro',zero_division=0)


def micro_f1_score(y_true,y_pred):
    return tf.py_function(np_micro_f1,(y_true,y_pred), tf.double)

