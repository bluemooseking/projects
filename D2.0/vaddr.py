# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 15:26:39 2018

@author: jhills
"""

class VADDR():
    def __init__(self, vmm):
        self._vmm = vmm
    
    def __getitem__(self, virt_addr):
        m_off = self._vmm.get_phys_mem_off(virt_addr)
        return self._vmm.PHYS_MEM[m_off]
        
    def __setitem__(self, virt_addr, val):
        m_off = self._vmm.get_phys_mem_off(virt_addr)
        self._vmm.PHYS_MEM[m_off] = val
