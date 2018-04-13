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
    
    def predict(self, vaddr, quant):
        if (quant > 0):
            return [vaddr + 1]
        else:
            return []

class PRED_HIST:
    mem_sacrifice_ratio = 0.1
    
    def __init__(self, pred_def):
        if 'ms_ratio' in pred_def:
            self.mem_sacrifice_ratio = pred_def['ms_ratio']
            
        self._vaddr_win = []
        self._vaddr_win_max = 1
        
        self._vaddr_link = {}
        self._vaddr_link_max = 1
        
    def _get_vaddr_window(self, vaddr):
        self._vaddr_win.append(vaddr)
        if len(self._vaddr_win) > self._vaddr_win_max:
            prev = self._vaddr_win.pop(0)
            return (prev, self._vaddr_win[:])
        else:
            return (None, self._vaddr_win[:])
    
    def _get_vaddr_link(self, vaddr):
        if vaddr in self._vaddr_link:
            return self._vaddr_link[vaddr][:]
        else:
            return None
        
    def _set_vaddr_link(self, vaddr, link):
        if vaddr not in self._vaddr_link:
            self._vaddr_link[vaddr] = []
        vlist = self._vaddr_link[vaddr]
        
        if link in vlist:
            vlist.insert(0, vlist.pop(vlist.index(link)))
        else:
            vlist.append(link)
            while len(vlist) > self._vaddr_link_max:
                vlist.pop(0)
            
    def get_pred_mem_size(self, mem_size):
        return int(self.mem_sacrifice_ratio * mem_size)
    
    
    def predict(self, vaddr, quant):
        ret = []
        prev_vaddr, window = self._get_vaddr_window(vaddr)
        
        if prev_vaddr:
            self._set_vaddr_link(prev_vaddr, vaddr)
        
        prev_virt_preds = self._get_vaddr_link(vaddr)        
        while quant:
            if not prev_virt_preds:
                break
            ret.append(prev_virt_preds.pop())
            quant -= 1
        return ret
