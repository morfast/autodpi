#!/usr/bin/python

import sys
from sklearn import svm
from sklearn.model_selection import cross_val_score
import glob


# truncate Truncate_size bytes from the front
Truncate_size = 3

def read_data_from_file(filename):

    global Truncate_size

    f = open(filename, "rb")
    rawdata = f.read()
    if len(rawdata) < Truncate_size:
        return []
    return [ord(b) for b in rawdata[:Truncate_size]]

def read_data():
    """ read data from tcpflow output files """

    data = []
    label = []
    for dirname in sys.argv[1:]:
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


def main():
    global Truncate_size

    for Truncate_size in range(1,32):
        x,y = read_data()
        
        clf = svm.SVC()
        clf.fit(x,y)
        scores = cross_val_score(clf, x, y, cv=5)
        print scores

main()
