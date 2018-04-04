# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 21:16:29 2018

@author: jhills
"""

import logging
import pandas as pd
import matplotlib.pyplot as plt

def vaddr_histogram(filename, data):
    data['vaddr'].hist(bins = 100)
    plt.title('Vaddr Histogram: %s' % (filename))
    plt.show()

def fault_type_cumulative(filename, data):
    onehot = pd.get_dummies(data['fault_type'])
    onehot.cumsum().plot()
    plt.title('Fault Types (Cumulative): %s' % (filename))
    plt.show()
    
def run_visuals(filename = None):
    if filename == None:
        logging.error("Specify filename")
        
    data = pd.read_csv(filename)
    vaddr_histogram(filename, data)
    fault_type_cumulative(filename, data)
    
#run_visuals('faults_treeA.csv')
#run_visuals('faults_seq.csv')
