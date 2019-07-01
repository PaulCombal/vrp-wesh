#!/bin/env python

import sys, random

if len(sys.argv) > 1:
    number_lines = int(sys.argv[1])
    xys = [random.sample(range(100), 2) for _ in range(number_lines)]
    num = 0
    with open("dataset2", "r+") as fp:
        for xy in xys:
            num = num + 1
            if num == number_lines:
                fp.write("%d %d" % (xy[0], xy[1]))
            else:
                fp.write("%d %d\n" % (xy[0], xy[1]))
