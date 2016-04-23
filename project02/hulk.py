#!/usr/bin/env python2.7

import hashlib, random, string, sys, getopt, itertools

# Constants

ALPHABET = string.ascii_lowercase + string.digits
LENGTH   = 8
#ATTEMPTS = nt(sys.argv[2])
HASHES   = "hashes.txt"
PREFIX   = ''

# Utility Functions
def usage(status=0):
    print '''Usage: hulk.py [-a ALPHABET -l LENGTH, -s HASHES, -p PREFIX]

    Options:
        -a  ALPHABET    Alphabet used for passwords
        -l  LENGTH      Length of passwords
        -s  HASHES      Path to file containing hashes
        -p  PREFIX      Prefix to user for each candidate password'''.format(os.path.basename(sys.argv[0]))
    sys.exit(status)

def md5sum(s):
    return hashlib.md5(s).hexdigest()

# Main Execution

if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha:l:s:p:")
    except getopt.GetoptError as err:
        print err
        usage(1)

    for o, a in opts:
        if o == '-a':
            ALPHABET = a
        elif o == '-l':
            LENGTH = int(a)
        elif o == '-s':
            HASHES = a
        elif o == '-p':
            PREFIX = a
        elif o == '-h':
            usage()
        else:
            usage(1)
    hashes = set([l.strip() for l in open(HASHES)])
    found  = set()

    candidates = [''.join(i) for i in itertools.product(ALPHABET, repeat = LENGTH)]
    
    for candidate in candidates:
       # print candidate
        candidate = PREFIX + candidate
        checksum  = md5sum(candidate)
        if checksum in hashes:
            found.add(candidate)

    for candidate in sorted(found):
        print candidate
