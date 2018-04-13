# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 16:23:54 2018

@author: jhills
"""

import logging
import random
from predictors import PRED_SEQ
from counter import COUNTER
from vaddr import VADDR

class VMM:
    # Debug Attributes
    logger = None
    fault_file = None
    
    # Physical Attributes
    PHYS_MEM_SIZE = None
    PHYS_BAK_SIZE = None
    VIRT_MEM_SIZE = None  

    # Data structures
    VIRT_ADDR_MODE = None
    VIRT_ADDR_OFFS = None
    LRU_VIRT_ADDR = None
    PHYS_MEM = None
    PHYS_BAK = None
    
    # Prediction
    PREDICTOR = None
      
    def init_fault_file(self, fault_file):
        if fault_file != None:
            self.fault_file = fault_file
            with open(self.fault_file, 'w') as the_file:
                the_file.write('vaddr,fault_type\n')
            
    def append_fault_file(self, vaddr, ftype):
        if self.fault_file != None:
            with open(self.fault_file, 'a') as the_file:
                the_file.write('%d,%s\n' % (vaddr, ftype))
 
    """
    =============================================
    INIT
    =============================================
    """       
    def __init_predictor(self, pred_def):
        if isinstance(pred_def, dict):
            if "mode" not in pred_def:
                raise ValueError('mode not specified in prediction dict')
                
            if pred_def["mode"] == 'seq':
                self.PREDICTOR = PRED_SEQ(pred_def)
                self._COUNTERS['PRED_SPACE_AVAIL'].val = self.PREDICTOR.get_pred_mem_size(self.PHYS_MEM_SIZE)
                
            else:
                raise ValueError(
                        'Invalid prediction mode: %s' % (pred_def['mode']))
                
        elif pred_def is not None:
            raise ValueError('Prediction def Bad Format')
            
    def __init__(self, phys_mem_size, phys_bak_size, 
                 fault_file = None,
                 pred_def = None,
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
        
        # Init Counters
        self._COUNTERS = {
                'CURR_ALLOC_SIZE':  COUNTER('Current Alloc Size', self.logger),
                'PRED_SPACE_AVAIL': COUNTER('Prediction Space Avail', self.logger),
                'PRED_WHEN_MEM':    COUNTER('Prediction when Mem', self.logger),
                'PRED_WHEN_PRED':   COUNTER('Prediction when Pred', self.logger),
                
                # Faults
                'FAULT_MAJ':        COUNTER('Fault - Major', self.logger),
                'FAULT_MIN':        COUNTER('Fault - Minor', self.logger),
                'FAULT_NONE':       COUNTER('Fault - None', self.logger),
        }
        # Init Data structs
        self.VIRT_ADDR_MODE = [None] * phys_all_size
        self.VIRT_ADDR_OFFS = [None] * phys_all_size
        self.LRU_VIRT_ADDR = [None] * phys_mem_size
        self.PHYS_MEM = [0] * phys_mem_size
        self.PHYS_BAK = [0] * phys_bak_size
        
        # Init Predictor
        self.__init_predictor(pred_def)
            
    """
    =============================================
    HELPER FUNCS
    =============================================
    """

    def get_alloc(self):
        val = self._COUNTERS['CURR_ALLOC_SIZE'].val
        self.logger.debug("current alloc = %d", val)
        return val
    
    def is_virt_addr(self, virt_addr):
        return (virt_addr < self._COUNTERS['CURR_ALLOC_SIZE'].val)
    
    def set_virt_addr_state(self, virt_addr, state, off):
        self.VIRT_ADDR_MODE[virt_addr] = state
        self.VIRT_ADDR_OFFS[virt_addr] = off
    
    def get_virt_addr_state(self, virt_addr):
        return (self.VIRT_ADDR_MODE[virt_addr], self.VIRT_ADDR_OFFS[virt_addr])
        
    def get_oldest_virt_addr(self):
        return self.LRU_VIRT_ADDR.pop()
    
    def set_newest_virt_addr(self, virt_addr):
        self.LRU_VIRT_ADDR.insert(0, virt_addr)
    
    def pop_specific_virt_addr(self, virt_addr):
        index = self.LRU_VIRT_ADDR.index(virt_addr)
        return self.LRU_VIRT_ADDR.pop(index)
        
    def lru_reset(self, virt_addr):
        self.set_newest_virt_addr(self.pop_specific_virt_addr(virt_addr))
        
    def __phys_swap(self, m_off, b_off):
        self.logger.debug("phys_swap: m(%d) <-> b(%d)", m_off, b_off)
        tmp = self.PHYS_MEM[m_off]
        self.PHYS_MEM[m_off] = self.PHYS_BAK[b_off]
        self.PHYS_BAK[b_off] = tmp
 
    """
    =============================================
    HELPER FUNCS 2.0
    =============================================
    """
       
    def fetch_to_mem(self, i_virt_addr, is_pred=False):      
        o_virt_addr = self.get_oldest_virt_addr()
        o_mode, o_off = self.get_virt_addr_state(o_virt_addr)
        i_mode, i_off = self.get_virt_addr_state(i_virt_addr)
        assert i_mode == 'bak'
        
        self.__phys_swap(o_off, i_off)
        
        if o_mode == "pred":
            self._COUNTERS['PRED_SPACE_AVAIL'].inc()
            
        self.set_virt_addr_state(o_virt_addr, "bak", i_off)
        
        self.set_newest_virt_addr(i_virt_addr)
        if is_pred:
            self.set_virt_addr_state(i_virt_addr, "pred", o_off)
        else:
            self.set_virt_addr_state(i_virt_addr, "mem", o_off)

        return o_off
    
    def enable_in_mem(self, virt_addr):
        mode, off = self.get_virt_addr_state(virt_addr)
        assert mode == "pred"
        self.set_virt_addr_state(virt_addr, "mem", off)
        self._COUNTERS['PRED_SPACE_AVAIL'].inc()
        self.lru_reset(virt_addr)
 
    def fetch_as_pred(self, virt_addr):
        if not self.is_virt_addr(virt_addr):
            return
        
        mode, off = self.get_virt_addr_state(virt_addr)
        if mode == "mem":
            self.lru_reset(virt_addr)
            self._COUNTERS['PRED_WHEN_MEM'].inc()
            
        elif mode == "pred":
            self.lru_reset(virt_addr)
            self._COUNTERS['PRED_WHEN_PRED'].inc()
            
        else:
            assert mode == 'bak'
            self.fetch_to_mem(virt_addr, is_pred = True)
            self._COUNTERS['PRED_SPACE_AVAIL'].dec()
        
    def fetch_preds(self, virt_addr):
        if self.PREDICTOR == None:
            return None
        space = self._COUNTERS['PRED_SPACE_AVAIL'].val
        for pred_vaddr in self.PREDICTOR.predict(virt_addr, space):
            self.fetch_as_pred(pred_vaddr)
        
    def get_phys_mem_off(self, virt_addr):
        mode, off = self.get_virt_addr_state(virt_addr)
        if mode == "bak":
            self._COUNTERS['FAULT_MAJ'].inc()
            self.append_fault_file(virt_addr, 'major')
            new_off = self.fetch_to_mem(virt_addr)
            self.fetch_preds(virt_addr) 
            return new_off
        
        elif mode == "pred":
            self._COUNTERS['FAULT_MIN'].inc()
            self.append_fault_file(virt_addr, 'minor')
            self.enable_in_mem(virt_addr)
            self.fetch_preds(virt_addr)  
            return off
        
        else:
            assert mode == "mem"
            self._COUNTERS['FAULT_NONE'].inc()
            self.append_fault_file(virt_addr, 'none')
            self.lru_reset(virt_addr)
            return off
                
    """
    =============================================
    CALLING FUNCS
    =============================================
    """
       
    def alloc_all(self):
        
        # Only do this once
        if self._COUNTERS['CURR_ALLOC_SIZE'].val != 0:
            self.logger.warning("alloc all: vmm not empty")
            return -1
        
        # Set it up
        self.logger.debug("alloc all = %d", self.VIRT_MEM_SIZE)
        self._COUNTERS['CURR_ALLOC_SIZE'].val = self.VIRT_MEM_SIZE
        
        for i in range(self.PHYS_MEM_SIZE):
            self.set_virt_addr_state(i, "mem", i)
            
        for i in range(self.PHYS_BAK_SIZE):
            self.set_virt_addr_state(i + self.PHYS_MEM_SIZE, "bak", i)
            
        self.LRU_VIRT_ADDR = list(range(self.PHYS_MEM_SIZE))
        
        mem = VADDR(self)
        return mem
    
    def get_counter_values(self):
        ret = []
        for counter in self._COUNTERS.values():
            ret.append((counter.name, counter.val))
        return ret

"""
=============================================
VALIDATE FUNCS
=============================================
"""
      
def validate_vmm(ll = logging.ERROR):
    mem_size = 20
    bak_size = 100
    all_size = mem_size + bak_size
    vmm = VMM(mem_size, bak_size, loglevel = ll, 
              fault_file = 'validate.csv',
              pred_def = {'mode' : 'seq'}
              )
    vmm.get_alloc()
    mem = vmm.alloc_all()
    
    data = random.sample(range(all_size * 100), all_size)
    for i in range(all_size):
        mem[i] = data[i]
    for i in range(all_size):
        if (data[i] != mem[i]):
            logging.critical("VMM VALIDATION FAILED")
    logging.critical("VMM VALIDATION PASSED")
