# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 11:57:57 2018

@author: jhills
"""

class PRED_SEQ:
    mem_sacrifice_ratio = 0.1
    
    def __init__(self, pred_def):
        if 'ms_ratio' in pred_def:
            self.mem_sacrifice_ratio = pred_def['ms_ratio']
    
    def get_pred_mem_size(self, mem_size):
        return int(self.mem_sacrifice_ratio * mem_size)
    
    def predict(self, virt_addr, quant):
        if (quant > 0):
            return [virt_addr + 1]
        else:
            return []
        