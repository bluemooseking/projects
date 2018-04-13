# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 13:56:18 2018

@author: jhills
"""

import logging
import random
from vmm import VMM

def test_sequential_array(filename = None,
                          pred_def = None,
                          test_def = None,
                          ):   
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
            return (False, vmm)
    return (True, vmm)
    
def test_binary_tree(filename = None,
                     pred_def = None,
                     test_def = None,
                     ):
      
    def _get_translate_table(depth):
        order = list(range(2 ** depth))
        random.shuffle(order)
        return order       
        
    tree_depth = 13
    tree_size = 2 ** tree_depth
    tree_mask = 2 ** (tree_depth - 2)
    m_ratio = 0.01
    m_loops = 5
    
    if ((test_def) and ('rand_translate' in test_def) and (test_def['rand_translate'])):
        vaddr_translate = _get_translate_table(tree_depth)
    else:
        vaddr_translate = list(range(2 ** tree_depth))
        
    m_size = int(tree_size * m_ratio)
    b_size = tree_size - m_size
    vmm = VMM(m_size, b_size, fault_file = filename, pred_def = pred_def)
    mem = vmm.alloc_all()
    for i in range(m_loops):
        for j in range(tree_size):
            vaddr = 0
            for k in range(tree_depth):
                mem[vaddr_translate[vaddr]]
                vaddr *= 2
                vaddr += 2 if ((j << k) & tree_mask) else 1
    return (True, vmm)
    
def run_test(name = None, testFunc = None, test_def = None,
             faultFile = None, pred_def = None):
    logging.critical("==============================================")
    logging.critical("%s BEGIN" % (name))
    ret, vmm = testFunc(faultFile, pred_def, test_def)
    if (ret):
        logging.critical("%s PASSED" % (name))
    else:
        logging.critical("%s FAILED" % (name))
        
    logging.critical("%s COUNTERS ->" % (name))
    for kvp in vmm.get_counter_values():
        logging.critical("%30s: %d" % kvp)
    
PREDS = [('P0-NONE',  None), 
         ('P1-SEQ',   {'mode' : 'seq'}),
         ('P2-HIST',  {'mode' : 'hist'}),
        ]
TESTS = [('T0-SEQ', test_sequential_array, None),
         ('T1-BIN', test_binary_tree, None),
         ('T2-BRND', test_binary_tree, {'rand_translate' : True}),
         ]
for (pname, pdef) in PREDS:
    for (tname, tfunc, tdef) in TESTS:
        run_test(name = "%s %s" % (tname, pname),
                 testFunc = tfunc,
                 test_def = tdef,
                 faultFile = "vmm.%s.%s.csv" % (tname, pname),
                 pred_def = pdef)
      
            
            