#!/usr/bin/python -u

import sys
import numpy as np
from copy import deepcopy

# evaluation
from sklearn.metrics import precision_recall_fscore_support
from sklearn import metrics
from sklearn.model_selection import train_test_split

# models
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import IsolationForest, RandomForestClassifier

# positvie and unlabelled classification
from puLearning.puAdapter import PUAdapter

class TrainingInfo(object):
    def __init__(self):
        pass

def read_sample_from_file(f, number = -1):
    res = []
    
    if number < 0:
        while True:
            length = f.read(1)
            if not length:
                break
            s = f.read(ord(length))
            res.append([ord(i) for i in s])
    else:
        n = 0
        while True:
            length =f.read(1)
            if not length:
                break
            length=ord(length)
            s = f.read(length)
            res.append([ord(i) for i in s])
	    
            n += 1
            if n >= number:
                break
    return res

def onehot_encode(data, const_len=64):
    """ expand n to a vector v with length 256, v[n] = 1, v[other] = 0 """
    res = []
    for n in data:
        ex = [0] * 257
        ex[n] = 1
        res += ex

    length=len(data)
    while length < const_len :
        res.extend([0] * 256)
        res.append(1)
        length += 1

    return res

def prepare_samples(pos_samples, neg_samples, test_ratio = 0.2, test_positive_only=False):
    """ get training set and testing set from the original sample data """
    pos_labels = [1] * len(pos_samples)
    neg_labels = [-1] * len(neg_samples)

    all_datas = pos_samples + neg_samples
    all_labels = pos_labels + neg_labels

    all_datas = [onehot_encode(d) for d in all_datas]

    train_data, test_data, train_label, test_label = \
        train_test_split(all_datas, all_labels, test_size = test_ratio)

    return np.array(train_data), np.array(test_data), \
            np.array(train_label), np.array(test_label)

def evaluate_model(y_test, y_pred):
    precision, recall, f1_score, _ = precision_recall_fscore_support(y_test, y_pred)
    print "precision/recall/F1: %4.3f %4.3f %4.3f" % (precision[1], recall[1], f1_score[1])

def pu_test(base_model, x_train, y_train, x_test, y_test):

    npos = len(np.where(y_train == 1)[0]) # index of positive samples
    n_sacrifice_iter = range(0, npos/5, npos/15)
    print n_sacrifice_iter
    for n_sacrifice in n_sacrifice_iter:

        # sacrifice positive samples to negtive
        print " ================= BEGIN ========================"
        print "Making %d positive examples negative" % (n_sacrifice)
        y_train_sac = np.copy(y_train)
        pos_idx = np.where(y_train == 1)[0] # index of positive samples
        sacrifice_idx = np.random.choice(pos_idx, n_sacrifice)
        y_train_sac[sacrifice_idx] = -1

        print "In test set: positive/negative: %d %d" % \
            (len(np.where(y_train_sac == 1)[0]), len(np.where(y_train_sac == -1)[0]))
        
        # fit with base model
        estimator = deepcopy(base_model)
        print "fitting base model ..."
        estimator.fit(x_train, y_train_sac)
        # predict with PU model
        y_pred = estimator.predict(x_test)
        evaluate_model(y_test, y_pred)
        print

        # fit with PU model
        estimator = deepcopy(base_model)
        pu_estimator = PUAdapter(estimator,hold_out_ratio=0.2)
        print "fitting PU model ..."
        pu_estimator.fit(x_train, y_train_sac)
        # predict with PU model
        y_pred = pu_estimator.predict(x_test)
        evaluate_model(y_test, y_pred)
        if n_sacrifice > 0:
            sac_test = x_train[sacrifice_idx] 
            sar_pred = pu_estimator.predict(sac_test)
            ratio = float(len(np.where(sar_pred == 1)[0])) / n_sacrifice
            print "recall for the sacrifice pos_samples:", ratio
        print " ================= END =========================="
        print


def parse_argument():
    if len(sys.argv) < 3:
        print "Usage: %s <pos> <neg>" % sys.argv[0]
        sys.exit(0)

    return sys.argv[1], sys.argv[2]


def main():

    # read sample from file
    pos_filename, neg_filename = parse_argument()
    pos_samples = read_sample_from_file(open(pos_filename), 100)
    neg_samples = read_sample_from_file(open(neg_filename), 1000)
    print "%d positive samples read from %s" % (len(pos_samples), pos_filename)
    print "%d negetive samples read from %s" % (len(neg_samples), neg_filename)

    # prepare samples
    print "preparing samples..."
    train_data, test_data, train_label, test_label = \
         prepare_samples(pos_samples, neg_samples)

    # train model
    base_model = GradientBoostingClassifier()
    print "begin test"
    pu_test(base_model, train_data, train_label, test_data, test_label)


main()
