# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 16:23:54 2018

@author: jhills
"""

import logging, sys
import random

class VMM:
    # Debug Attributes
    logger = None
    fault_file = None
    
    # Physical Attributes
    PHYS_MEM_SIZE = None
    PHYS_BAK_SIZE = None
    VIRT_MEM_SIZE = None
    
    # State Variable
    CURRENT_ALLOC_SIZE = None

    # Data structures
    VIRT_ADDR_MODE = None
    VIRT_ADDR_OFFS = None
    LRU_VIRT_ADDR = None
    PHYS_MEM = None
    PHYS_BAK = None
      
    def init_fault_file(self, fault_file):
        if fault_file != None:
            self.fault_file = fault_file
            with open(self.fault_file, 'w') as the_file:
                the_file.write('vaddr,fault_type\n')
            
    def append_fault_file(self, vaddr, ftype):
        if self.fault_file != None:
            with open(self.fault_file, 'a') as the_file:
                the_file.write('%d,%s\n' % (vaddr, ftype))
            
    def __init__(self, phys_mem_size, phys_bak_size, 
                 fault_file = None,
                 loglevel = logging.ERROR):
        # Init Debug
        self.logger = logging.getLogger('vmm')
        self.logger.setLevel(loglevel)
        self.logger.debug("Welcome to VMM logger")
        self.init_fault_file(fault_file)    
        
        # Init Physical
        phys_all_size = phys_mem_size + phys_bak_size
        self.PHYS_MEM_SIZE = phys_mem_size
        self.PHYS_BAK_SIZE = phys_bak_size
        self.VIRT_MEM_SIZE = phys_all_size
        self.logger.debug("Mem Size: %d", self.PHYS_MEM_SIZE)
        self.logger.debug("Bak Size: %d", self.PHYS_BAK_SIZE)
        
        # Init Stete Vars
        self.CURRENT_ALLOC_SIZE = 0
        
        # Init Data structs
        self.VIRT_ADDR_MODE = [None] * phys_all_size
        self.VIRT_ADDR_OFFS = [None] * phys_all_size
        self.LRU_VIRT_ADDR = [None] * phys_mem_size
        self.PHYS_MEM = [0] * phys_mem_size
        self.PHYS_BAK = [0] * phys_bak_size
      
    def get_alloc(self):
        self.logger.debug("current alloc = %d", self.CURRENT_ALLOC_SIZE)
        return self.CURRENT_ALLOC_SIZE
    
    def alloc_all(self):
        
        # Only do this once
        if self.CURRENT_ALLOC_SIZE != 0:
            self.logger.warning("alloc all: vmm not empty")
            return -1
        
        # Set it up
        self.logger.debug("alloc all = %d", self.VIRT_MEM_SIZE)
        self.CURRENT_ALLOC_SIZE = self.VIRT_MEM_SIZE
        for i in range(self.PHYS_MEM_SIZE):
            self.VIRT_ADDR_MODE[i] = "mem"
            self.VIRT_ADDR_OFFS[i] = i
        for i in range(self.PHYS_BAK_SIZE):
            self.VIRT_ADDR_MODE[i + self.PHYS_MEM_SIZE] = "bak"
            self.VIRT_ADDR_OFFS[i + self.PHYS_MEM_SIZE] = i
        self.LRU_VIRT_ADDR = list(range(self.PHYS_MEM_SIZE))
        
        return 0
    
    def swap(self, m_off, b_off):
        self.logger.debug("swap: m(%d) <-> b(%d)", m_off, b_off)
        tmp = self.PHYS_MEM[m_off]
        self.PHYS_MEM[m_off] = self.PHYS_BAK[b_off]
        self.PHYS_BAK[b_off] = tmp
        
    def restore(self, virt_addr):
        assert self.VIRT_ADDR_MODE[virt_addr] == "bak"
        
        old_virt_addr = self.LRU_VIRT_ADDR.pop()
        m_off = self.VIRT_ADDR_OFFS[old_virt_addr]
        b_off = self.VIRT_ADDR_OFFS[virt_addr]
        
        self.swap(m_off, b_off)
        self.LRU_VIRT_ADDR.insert(0, virt_addr)
        self.VIRT_ADDR_MODE[old_virt_addr] = "bak"
        self.VIRT_ADDR_OFFS[old_virt_addr] = b_off
        self.VIRT_ADDR_MODE[virt_addr] = "mem"
        self.VIRT_ADDR_OFFS[virt_addr] = m_off
        
        return m_off
        
    def get_phys_mem_off(self, virt_addr):
        if (self.VIRT_ADDR_MODE[virt_addr] == "bak"):
            self.append_fault_file(virt_addr, 'major')
            return self.restore(virt_addr)
        else:
            self.append_fault_file(virt_addr, 'none')
            index = self.LRU_VIRT_ADDR.index(virt_addr)
            self.LRU_VIRT_ADDR.insert(0, self.LRU_VIRT_ADDR.pop(index))
            return self.VIRT_ADDR_OFFS[virt_addr]
            
        
    def read(self, virt_addr):
        m_off = self.get_phys_mem_off(virt_addr)
        return self.PHYS_MEM[m_off]
        
    def write(self, virt_addr, val):
        m_off = self.get_phys_mem_off(virt_addr)
        self.PHYS_MEM[m_off] = val
        
def __validate_vmm(ll = logging.DEBUG):
    vmm = VMM(5, 10, loglevel = ll, fault_file = 'validate.csv')
    vmm.get_alloc()
    vmm.alloc_all()
    
    data = random.sample(range(100), 15)
    for i in range(15):
        vmm.write(i, data[i])
    for i in range(15):
        if (data[i] != vmm.read(i)):
            logging.critical("VMM VALIDATION FAILED")
    logging.critical("VMM VALIDATION PASSED")
    
def validate_vmm():
    __validate_vmm(ll = logging.ERROR)