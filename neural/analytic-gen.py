# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 14:15:41 2018

@author: jhills
"""

import numpy as np
import math
import csv

end  = 10
step = 0.00001

x = np.arange(step, end, step)
xdata = np.concatenate((
        np.array([["x","sin","cos","exp","log"]]),
        np.column_stack((
                x,
                np.sin(x),
                np.cos(x),
                np.exp(x),
                np.log(x)
        ))), axis=0)

with open('analytic.data.csv', "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n", delimiter=',')
        writer.writerows(xdata)
        csv_file.close
