# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 14:15:41 2018

@author: jhills
"""

import numpy as np
import csv

end  = 1
step = 0.001

r = np.arange(step, end, step)
av, bv = np.meshgrid(r, r, sparse=False)
a = av.reshape((-1,1))
b = bv.reshape((-1,1))

xdata = np.concatenate((
        np.array([["a","b","div","mod"]]),
        np.column_stack((
                a,
                b,
                np.floor_divide(a,b),
                np.remainder(a,b)
        ))), axis=0)

with open('divmod.data.csv', "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n", delimiter=',')
        writer.writerows(xdata)
        csv_file.close