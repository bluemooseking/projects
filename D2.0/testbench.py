# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 13:56:18 2018

@author: jhills
"""

import logging
import random
from vmm import VMM

def test_sequential_array(filename = None,
                          pred_def = None):   
    data_size = 1000
    m_ratio = 0.1
    m_loops = 100
    
    m_size = int(data_size * m_ratio)
    b_size = data_size - m_size
    vmm = VMM(m_size, b_size, fault_file = filename, pred_def = pred_def)
    mem = vmm.alloc_all()
    data = random.sample(range(data_size * 100), data_size)
    for i in range(m_loops):
        for j in range(data_size):
            mem[j] = data[j] + i
    for j in range(data_size):
        if (data[j] + m_loops - 1 != mem[j]):
            return False
    return True
    
def test_binary_tree(filename = None,
                     pred_def = None):    
    tree_depth = 10
    tree_size = 2 ** tree_depth
    tree_mask = 2 ** (tree_depth - 2)
    m_ratio = 0.01
    m_loops = 5
    
    m_size = int(tree_size * m_ratio)
    b_size = tree_size - m_size
    vmm = VMM(m_size, b_size, fault_file = filename, pred_def = pred_def)
    mem = vmm.alloc_all()
    for i in range(m_loops):
        for j in range(tree_size):
            vaddr = 0
            for k in range(tree_depth):
                mem[vaddr]
                vaddr *= 2
                vaddr += 2 if ((j << k) & tree_mask) else 1
    return True
    
def run_test(name = None, testFunc = None,
             faultFile = None, pred_def = None):
    logging.critical("%s BEGIN" % (name))
    if testFunc(faultFile, pred_def):
        logging.critical("%s PASSED" % (name))
    else:
        logging.critical("%s FAILED" % (name))

run_test("SEQ PREDNONE", test_sequential_array, 'faults_seq_Pnone.csv')
run_test("BIN PREDNONE", test_binary_tree, 'faults_treeA_Pnone.csv') 
run_test("SEQ PREDSEQ", test_sequential_array, 
         'faults_seq_Pseq.csv', pred_def = {'mode' : 'seq'})
run_test("BIN PREDSEQ", test_binary_tree, 
         'faults_treeA_Pseq.csv', pred_def = {'mode' : 'seq'})         
            
            