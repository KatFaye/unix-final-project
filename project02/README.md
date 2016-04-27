Project 02: Distributed Computing
=================================

1. hulk.py works by first parsing the needed command line 
arguments of length as well as hashes or prefixes if any are 
supplied. The hashes file is opened, and each line is stripped 
and stored into the set hashes.

From there, hulk iterates over the alphabet with a given prefix 
to create a set of candidate passwords. The checksum is found 
with md5sum, and if that value is in hashes, then the candidate 
is added to the set of passwords found.

I tested it by running the program on small values and checking 
the expected values were outputted, as well as running it on 
hashes.txt

2. Fury.py utilitizes hulk to crack the passwords by
 creating a series of commands that call hulk.py with various 
 prefixes and storing the values in a journal. These prefixes 
 allow the work of hulk.py to be divided up amongst different 
 workers for lengthier passwords. Fury uses a log to track which 
 passwords have been attempted, and updates an ongoing 
 collection of passwords in order to recover from failures. I 
 tested fury.py by running it with smaller-length arguments to 
 hulk and verifying the results; however, it took several days 
 to notice a bug where I was naming the output file incorrectly.

3. It would be more difficult to crack a passwords of greater 
length due to the fact that complecity with respect to length is 
exponential, whereas it's linear for alphabet size.