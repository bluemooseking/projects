# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 14:15:41 2018

@author: jhills
"""

import numpy as np
import csv

trials_per = 1000      # will end up with trials_per^2 datapoints

indicator_count = 9
def vrange(starts_and_ends):
    ret = np.array(())
    for x in starts_and_ends:
        ret = np.append(ret,np.linspace(x[0], 
                                        x[1], 
                                        indicator_count, 
                                        endpoint=True))
    return ret.reshape(-1, indicator_count)


d = np.dstack(
        np.meshgrid(
                np.linspace(0, 2*np.pi, trials_per, endpoint=True),
                np.linspace(0, 2*np.pi, trials_per, endpoint=True),
                sparse=False)
        ).reshape(-1,2)
        
xdata = np.sin(vrange(d))

with open('trigpred.data.csv', "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n", delimiter=',')
        writer.writerows(xdata)
        csv_file.close
