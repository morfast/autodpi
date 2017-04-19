#!/usr/bin/python

import sys
import glob
from numpy import mean
import argparse

from sklearn import svm
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import SGDClassifier
from sklearn import neighbors
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn import tree


# truncate Truncate_size bytes from the front
Truncate_size = 5

def read_data_from_file(filename):

    global Truncate_size

    skip_size = 0

    f = open(filename, "rb")
    rawdata = f.read()
    if len(rawdata) < skip_size + Truncate_size:
        return []
    return [ord(b) for b in rawdata[skip_size:skip_size+Truncate_size]]

def read_data(dirnames):
    """ read data from tcpflow output files """

    data = []
    label = []
    for dirname in dirnames:
        dirname = dirname.strip('/')
        # get data file list
        filelist = glob.glob(dirname + "/*-*")
        processed_file = {}
        for filename in filelist:
            basefilename = filename.split('/')[1]
            # is this a mirror file that has been processed ?
            if processed_file.has_key(basefilename):
                continue
            mirror_basefilename = "-".join(basefilename.split('-')[::-1])
            mirror_filename = "/".join([dirname, mirror_basefilename])
            # mirror file exist ?
            if mirror_filename in filelist:
                a = read_data_from_file(filename)
                b = read_data_from_file(mirror_filename)
                if a and b:
                    data.append(a + b)
                    label.append(dirname)
                processed_file[basefilename] = 1
                processed_file[mirror_basefilename] = 1

    return data, label

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--train", action='store', nargs='*')
    parser.add_argument("-d", "--data", action='store', nargs='*')

    args =  parser.parse_args()

    return args

def main():
    global Truncate_size

    for Truncate_size in range(1,16):
        x,y = read_data()
        
        #clf = svm.SVC()
        #clf = SGDClassifier()
        #clf = neighbors.KNeighborsClassifier(8, 'distance')
        #clf = GaussianNB()
        #clf = MLPClassifier(solver='lbfgs', alpha=1e-5, \
        #                    hidden_layer_sizes=(5, 2), random_state=1)
        clf = tree.DecisionTreeClassifier()
        clf.fit(x,y)
        scores = cross_val_score(clf, x, y, cv=5)
        print mean(scores)

def svmtest():
    args = parse_arguments()

    x,y = read_data(args.train)
    data_dict = {}
    for elem in zip(y,x):
        key, value = elem
        if data_dict.has_key(key):
            data_dict[key].append(value)
        else:
            data_dict[key] = [value, ]

    clfs = []
    for key in data_dict.keys():
        # key is type, value is data
        clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
        #clf = svm.OneClassSVM()
        clf.fit(data_dict[key])
        clfs.append((key, clf))

    x,y = read_data(args.data)
    for clfname, clf in clfs:
        print float(len([i for i in clf.predict(x) if i == 1]))/len(x)


#main()
clfs = svmtest()
