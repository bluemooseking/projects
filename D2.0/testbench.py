# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 13:56:18 2018

@author: jhills
"""

import logging, sys
import random
from vmm import VMM, validate_vmm
validate_vmm()

def gen_sequential_array_faults(filename = None):
    if filename == None:
        logging.error("Specify filename")
    
    data_size = 1000
    m_ratio = 0.1
    m_loops = 100
    
    m_size = int(data_size * m_ratio)
    b_size = data_size - m_size
    vmm = VMM(m_size, b_size, fault_file = filename)
    vmm.alloc_all()
    data = random.sample(range(data_size * 100), data_size)
    for i in range(m_loops):
        for j in range(data_size):
            vmm.write(j, data[j] + i)
    for j in range(data_size):
        if (data[j] + m_loops - 1 != vmm.read(j)):
            logging.critical("SEQ VALIDATION FAILED")
    logging.critical("SEQ VALIDATION PASSED")
    
def gen_binary_tree_faults_A(filename = None):
    if filename == None:
        logging.error("Specify filename")
    
    tree_depth = 15
    tree_size = 2 ** tree_depth
    tree_mask = 2 ** (tree_depth - 2)
    m_ratio = 0.01
    m_loops = 5
    
    m_size = int(tree_size * m_ratio)
    b_size = tree_size - m_size
    vmm = VMM(m_size, b_size, fault_file = filename)
    vmm.alloc_all()
    for i in range(m_loops):
        for j in range(tree_size):
            vaddr = 0
            for k in range(tree_depth):
                vmm.read(vaddr)
                vaddr *= 2
                vaddr += 2 if ((j << k) & tree_mask) else 1
                
gen_binary_tree_faults_A('faults_treeA.csv')          
            
            