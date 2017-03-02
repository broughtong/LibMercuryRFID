import time
import sys
#import random

args = sys.argv
del args[0]

for i in xrange(0, int(args[0])):
	execfile('rotate.py')
	time.sleep(2)
	print i
