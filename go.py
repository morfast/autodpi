#!/usr/bin/python -u

import sys
import glob
from numpy import mean
import argparse
import operator
import re
import random

from sklearn import svm
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import SGDClassifier
from sklearn import neighbors
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn import tree
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

from mybayes import MyBayesClassifier

# truncate Truncate_size bytes from the front
Truncate_size = 32
Max_Round_count = 1

def read_data(dirnames):
    """ read data from tcpflow output files """

    data = []
    label = []
    for dirname in dirnames:
        dirname = dirname.strip('/')
        # get data file list
        filelist = glob.glob(dirname + "/*-*")
        filelist.sort()
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


def read_data_from_file(filename):

    global Truncate_size

    skip_size = 0

    f = open(filename, "rb")
    rawdata = f.read()
    if len(rawdata) < skip_size + Truncate_size:
        return []
    return [ord(b) for b in rawdata[skip_size:skip_size+Truncate_size]]

def expand_to_bit_data(data):
    """ expand n to a vector v with length 256, v[n] = 1, v[other] = 0 """
    res = []
    for n in data:
        ex = [0] * 257
        ex[n] = 1
        res += ex

    return res

def read_data_from_tshark_file(filename):
    global Max_Round_count
    global Truncate_size

    lines = open(filename).readlines()
    state = 'tab'
    data = []
    rcount = 0 # round count
    for line in lines[6:-1]:
        if line[0] != "\t":
            d = [int(i, 16) for i in re.findall('..', line)]
            if state == 'tab':
                data += d[:Truncate_size] + [256] * (Truncate_size - len(d[:Truncate_size]))
                state = 'notab'
        else:
            d = [int(i, 16) for i in re.findall('..', line[1:])]
            if state == 'notab':
                data += d[:Truncate_size] + [256] * (Truncate_size - len(d[:Truncate_size]))
                state = 'tab'
                rcount += 1
                if rcount >= Max_Round_count:
                    break

    if not (len(data) == 0 or len(data) == Truncate_size*2):
        return []
        print len(data)
        print filename
    assert(len(data) == 0 or len(data) == Truncate_size*2)
    return expand_to_bit_data(data)

def read_data_tshark(dirnames):
    """ read data from tshark output files """

    data = []
    label = []
    for dirname in dirnames:
        dirname = dirname.strip('/')
        # get data file list
        filelist = glob.glob(dirname + "/flow*")
        ndata = 0
        for filename in filelist:
            a = read_data_from_tshark_file(filename)
            if a:
                data.append(a)
                label.append(dirname)
                ndata += 1
        print dirname, len(filelist), ndata

    return data, label

def count_elem(data):
    
    res = {}
    for d in data:
        if d in res.keys():
            res[d] += 1
        else:
            res[d] = 1
    return res

def clustering(input_data):
    #clf = AffinityPropagation(preference=-50)
    #clf = AffinityPropagation()
    data = StandardScaler().fit_transform(input_data)
    clf = DBSCAN(min_samples=3, eps=0.3)
    clf.fit(data)
    print clf.labels_
    sorted_x = sorted(count_elem(clf.labels_).items(), key=operator.itemgetter(1))
    sorted_x.reverse()
    print sorted_x

def test_clustering():
    x = [[1,1,], [2,2], [1,2], [8,9], [7,9], [8,8]]
    print x
    x = StandardScaler().fit_transform(x)
    print x
    clustering(x)

    

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--train", action='store', nargs='*')
    parser.add_argument("-d", "--data", action='store', nargs='*')

    args =  parser.parse_args()

    return args

def single_classifier_test():
    global Truncate_size

    args = parse_arguments()
    for Truncate_size in range(10,95,10):
        x,y = read_data_tshark(args.train)
        print len(x)
        
        #clf = svm.SVC()
        #clf = SGDClassifier()
        #clf = neighbors.KNeighborsClassifier(8, 'distance')
        #clf = GaussianNB()
        clf = MLPClassifier(solver='lbfgs', alpha=1e-5, \
                            hidden_layer_sizes=(5, 2), random_state=1)
        #clf = tree.DecisionTreeClassifier()
        clf.fit(x,y)
        scores = cross_val_score(clf, x, y, cv=4)
        print mean(scores)

def coef_analysis(coef):
    mod = 256
    n_large = 0
    for i, c in enumerate(coef):
        if abs(c) > 2 * 10e-2:
            n_large += 1
            print (i+1) % mod, 
        if i > 0 and ((i+1) % mod == 0):
            print "| ", n_large
            n_large = 0
    print

def shuffle_data(x,y):
    s = zip(x, y)
    random.shuffle(s)
    return [a[0] for a in s], [a[1] for a in s]

def fill_with_random(x):
    length = len(x)/256
    #return expand_to_bit_data([random.randint(0,255) for i in range(length)])
    return expand_to_bit_data([0 for i in range(length)])

def multiple_classifier_test():
    global Truncate_size
    args = parse_arguments()

    print "reading training data ..."
    x,y = read_data_tshark(args.train)
    classes = set(y)
    print "number of training data:", len(x)
    print "number of classes:", len(classes)

    x,y = shuffle_data(x, y)
    
    for c in classes:
        xx = x[:]
        yy = y[:]
        for i,cname in enumerate(yy):
            if cname == c:
                yy[i] = 1
            else:
                yy[i] = -1
                #xx[i] = fill_with_random(xx[i])
        clf = GaussianNB()
        #clf = MLPClassifier(activation='relu', solver='adam', alpha=1e-5, \
        #                    hidden_layer_sizes=(), random_state=1, max_iter=1500)
        #print clf.get_params()
        #print len(xx[0])

        #coef_analysis(clf.coefs_[0])
        scores = cross_val_score(clf, xx, yy, cv=4)
        print c, scores, mean(scores)

        #clf = MyBayesClassifier()
        #clf.fit(xx,yy)

        #predict_y = clf.predict(xx)
        #c = 0
        #for i, ry in enumerate(yy):
        #    if predict_y[i] == ry:
        #        c += 1

        #print float(c)/len(yy)

def outlier_test():
    args = parse_arguments()

    x,y = read_data_tshark(args.train)
    print "size of training set:", len(x)

    # class_name: [data]
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
        #clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
        #clf = IsolationForest()
        clf = svm.OneClassSVM()
        clf.fit(data_dict[key])
        clfs.append((key, clf))

    x,y = read_data_tshark(args.data)
    print "size of test set:", len(x)
    #for line in x:
    #    print "\t".join(["%02x" % a for a in line])
    for clfname, clf in clfs:
        print clf.predict(x)
        print float(len([i for i in clf.predict(x) if i == 1]))/len(x)

#single_classifier_test()
multiple_classifier_test()
#clfs = svmtest()
#test_clustering()
#outlier_test()
#print expand_to_bit_data([1,2])
