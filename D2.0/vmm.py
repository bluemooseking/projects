# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 16:23:54 2018

@author: jhills
"""

import logging, sys

class VMM:
    # Debug Attributes
    logger = None
    
    # Physical Attributes
    PHYS_MEM_SIZE = None
    PHYS_BAK_SIZE = None
    VIRT_MEM_SIZE = None
    
    # State Variable
    CURRENT_ALLOC_SIZE = None

    # Data structures
    VIRT_ADDR_TABLE = None
    PHYS_MEM = None
    PHYS_BAK = None
    
    class ADDR_TABLE_ENTRY:
        phys_addr = None
        phys_mode = None
        def __init__(self, addr, mode):
            phys_addr = addr
            phys_mode = mode
            
    def __init__(self, phys_mem_size, phys_bak_size, 
                 loglevel = logging.ERROR):
        # Init Debug
        self.logger = logging.getLogger('vmm')
        self.logger.setLevel(loglevel)
        self.logger.debug("Welcome to VMM logger")
        
        # Init Physical
        phys_all_size = phys_mem_size + phys_bak_size
        self.PHYS_MEM_SIZE = phys_mem_size
        self.PHYS_BAK_SIZE = phys_bak_size
        self.VIRT_MEM_SIZE = phys_all_size
        
        # Init Stete Vars
        self.CURRENT_ALLOC_SIZE = 0
        
        # Init Data structs
        self.VIRT_ADDR_TABLE = dict.fromkeys(range(phys_all_size), 0)
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
        self.logger.debug("alloc all = %d", self.CURRENT_ALLOC_SIZE)
        self.CURRENT_ALLOC_SIZE = self.VIRT_MEM_SIZE
            
        return 0
    
    #def read(self, virt_addr):
        
    #def write(self, virt_addr, val):
        
        
vmm = VMM(1000, 10000, loglevel = logging.DEBUG)
vmm.get_alloc()
vmm.alloc_all()
vmm.alloc_all()
vmm.get_alloc()
 