# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 16:23:54 2018

@author: jhills
"""

import logging
import random
from predictors import PRED_SEQ, PRED_HIST
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
    VADDR_MODE = None
    VADDR_OFFS = None
    LRU_VADDR = None
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
                
            elif pred_def["mode"] == 'hist':
                self.PREDICTOR = PRED_HIST(pred_def)
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
                'PRED_WHEN_BAK':    COUNTER('Prediction when Bak', self.logger),
                
                # Faults
                'FAULT_MAJ':        COUNTER('Fault - Major', self.logger),
                'FAULT_MIN':        COUNTER('Fault - Minor', self.logger),
                'FAULT_NONE':       COUNTER('Fault - None', self.logger),
        }
        # Init Data structs
        self.VADDR_MODE = [None] * phys_all_size
        self.VADDR_OFFS = [None] * phys_all_size
        self.LRU_VADDR = [None] * phys_mem_size
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
    
    def is_vaddr(self, vaddr):
        return (vaddr < self._COUNTERS['CURR_ALLOC_SIZE'].val)
    
    def set_vaddr_state(self, vaddr, state, off):
        self.VADDR_MODE[vaddr] = state
        self.VADDR_OFFS[vaddr] = off
    
    def get_vaddr_state(self, vaddr):
        return (self.VADDR_MODE[vaddr], self.VADDR_OFFS[vaddr])
        
    def get_oldest_vaddr(self):
        return self.LRU_VADDR.pop()
    
    def set_newest_vaddr(self, vaddr):
        self.LRU_VADDR.insert(0, vaddr)
    
    def pop_specific_vaddr(self, vaddr):
        index = self.LRU_VADDR.index(vaddr)
        return self.LRU_VADDR.pop(index)
        
    def lru_reset(self, vaddr):
        self.set_newest_vaddr(self.pop_specific_vaddr(vaddr))
        
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
       
    def fetch_to_mem(self, i_vaddr, is_pred=False):      
        o_vaddr = self.get_oldest_vaddr()
        o_mode, o_off = self.get_vaddr_state(o_vaddr)
        i_mode, i_off = self.get_vaddr_state(i_vaddr)
        assert i_mode == 'bak'
        
        self.__phys_swap(o_off, i_off)
        
        if o_mode == "pred":
            self._COUNTERS['PRED_SPACE_AVAIL'].inc()
            
        self.set_vaddr_state(o_vaddr, "bak", i_off)
        
        self.set_newest_vaddr(i_vaddr)
        if is_pred:
            self.set_vaddr_state(i_vaddr, "pred", o_off)
        else:
            self.set_vaddr_state(i_vaddr, "mem", o_off)

        return o_off
    
    def enable_in_mem(self, vaddr):
        mode, off = self.get_vaddr_state(vaddr)
        assert mode == "pred"
        self.set_vaddr_state(vaddr, "mem", off)
        self._COUNTERS['PRED_SPACE_AVAIL'].inc()
        self.lru_reset(vaddr)
 
    def fetch_as_pred(self, vaddr):
        if not self.is_vaddr(vaddr):
            return
        
        mode, off = self.get_vaddr_state(vaddr)
        if mode == "mem":
            self.lru_reset(vaddr)
            self._COUNTERS['PRED_WHEN_MEM'].inc()
            
        elif mode == "pred":
            self.lru_reset(vaddr)
            self._COUNTERS['PRED_WHEN_PRED'].inc()
            
        else:
            assert mode == 'bak'
            self.fetch_to_mem(vaddr, is_pred = True)
            self._COUNTERS['PRED_WHEN_BAK'].inc()
            self._COUNTERS['PRED_SPACE_AVAIL'].dec()
        
    def fetch_preds(self, vaddr):
        if self.PREDICTOR == None:
            return None
        space = self._COUNTERS['PRED_SPACE_AVAIL'].val
        for pred_vaddr in self.PREDICTOR.predict(vaddr, space):
            self.fetch_as_pred(pred_vaddr)
        
    def get_phys_mem_off(self, vaddr):
        mode, off = self.get_vaddr_state(vaddr)
        if mode == "bak":
            self._COUNTERS['FAULT_MAJ'].inc()
            self.append_fault_file(vaddr, 'major')
            new_off = self.fetch_to_mem(vaddr)
            self.fetch_preds(vaddr) 
            return new_off
        
        elif mode == "pred":
            self._COUNTERS['FAULT_MIN'].inc()
            self.append_fault_file(vaddr, 'minor')
            self.enable_in_mem(vaddr)
            self.fetch_preds(vaddr)  
            return off
        
        else:
            assert mode == "mem"
            self._COUNTERS['FAULT_NONE'].inc()
            self.append_fault_file(vaddr, 'none')
            self.lru_reset(vaddr)
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
            self.set_vaddr_state(i, "mem", i)
            
        for i in range(self.PHYS_BAK_SIZE):
            self.set_vaddr_state(i + self.PHYS_MEM_SIZE, "bak", i)
            
        self.LRU_VADDR = list(range(self.PHYS_MEM_SIZE))
        
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
