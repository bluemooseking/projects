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

class PRED_HIST:
    mem_sacrifice_ratio = 0.1
    
    def __init__(self, pred_def):
        if 'ms_ratio' in pred_def:
            self.mem_sacrifice_ratio = pred_def['ms_ratio']
            
        self._vaddr_win = []
        self._vaddr_win_max = 1
        
        self._vaddr_link = {}
        self._vaddr_link_max = 1
        
    def _get_vaddr_window(self, virt_addr):
        self._vaddr_win.append(virt_addr)
        if len(self._vaddr_win) > self._vaddr_win_max:
            prev = self._vaddr_win.pop(0)
            return (prev, self._vaddr_win[:])
        else:
            return (None, self._vaddr_win[:])
    
    def _get_vaddr_link(self, virt_addr):
        if virt_addr in self._vaddr_link:
            return self._vaddr_link[virt_addr][:]
        else:
            return None
        
    def _set_vaddr_link(self, virt_addr, link):
        if virt_addr not in self._vaddr_link:
            self._vaddr_link[virt_addr] = []
        vlist = self._vaddr_link[virt_addr]
        
        if link in vlist:
            vlist.insert(0, vlist.pop(vlist.index(link)))
        else:
            vlist.append(link)
            while len(vlist) > self._vaddr_link_max:
                vlist.pop(0)
            
    def get_pred_mem_size(self, mem_size):
        return int(self.mem_sacrifice_ratio * mem_size)
    
    
    def predict(self, virt_addr, quant):
        ret = []
        prev_virt_addr, window = self._get_vaddr_window(virt_addr)
        
        if prev_virt_addr:
            self._set_vaddr_link(prev_virt_addr, virt_addr)
        
        prev_virt_preds = self._get_vaddr_link(virt_addr)        
        while quant:
            if not prev_virt_preds:
                break
            ret.append(prev_virt_preds.pop())
            quant -= 1
        return ret
