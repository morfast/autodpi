#!/usr/bin/python

import sys

def save_sample_to_file(f, sample):
    """ save sample to file """
    s = bytearray([int(i,16) for i in sample])
    s.insert(0, len(s))
    f.write(s)

def read_sample_from_file(f):
    res = []
    while True:
        length = f.read(1)
        if not length:
            break
        s = f.read(ord(length))
        res.append([ord(i) for i in s])
    return res


def main():

    nline_to_skip = 3
    nbyte_to_skip = 10
    
    
    # save samples to this file
    ofile = open(sys.argv[1], "wb")
    
    n_line = 0
    sample = []
    for line in sys.stdin:
    
        if len(line.strip()) == 0:
            save_sample_to_file(ofile, sample)
            n_line = 0
            sample = []
            continue
    
        n_line += 1
        if n_line < nline_to_skip:
            # skip lines
            continue
        elif n_line == nline_to_skip:
            # skip bytes
            body = line[6:53]
            sample += body.split()[nbyte_to_skip:]
        else:
            body = line[6:53]
            sample += body.split()

    ofile.close()


main()

#ifile = open(sys.argv[1], 'rb')
#read_sample_from_file(ifile)
