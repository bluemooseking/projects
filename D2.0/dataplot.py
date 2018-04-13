# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 21:16:29 2018

@author: jhills
"""
import numpy as np
import logging
import pandas as pd
import matplotlib.pyplot as plt
import os

def vaddr_histogram(filename, data):
    data['vaddr'].hist(bins = 100)
    plt.title('Vaddr Histogram: %s' % (filename))
    plt.xlabel('vaddr')
    plt.ylabel('hit count')
    plt.show()

def fault_type_cumulative(filename, data):
    one_hot = pd.get_dummies(data['fault_type'])
    cum_sum = np.array(one_hot).cumsum(axis=0)
    plt.stackplot(np.array(range(len(one_hot))), 
                  (cum_sum/cum_sum.sum(axis=1, keepdims=True)).T, 
                  labels = one_hot.columns)
    plt.title('Fault Types (Cumulative): %s' % (filename))
    plt.xlabel('fault count')
    plt.legend(loc = 2)
    plt.show()
    
def run_visuals(filename = None):
    if filename == None:
        logging.error("Specify filename")
        
    data = pd.read_csv(filename)
    vaddr_histogram(filename, data)
    fault_type_cumulative(filename, data)

for file in os.listdir():
    if file.endswith(".csv"):
        run_visuals(file)
