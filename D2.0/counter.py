# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 14:33:56 2018

@author: jhills
"""

class COUNTER:
    def __init__(self, name = None, logger = None):
        self._logger = logger
        self._val = 0
        self._name = name
        self._dlog("init(%s) = %d", 
                self._name, self._val)
    def _dlog(self, *args):
        if self._logger is None:
            return
        self._logger.debug(*args)
    @property
    def val(self):
        self._dlog("get(%s) = %d", 
                self._name, self._val)
        return self._val
    @val.setter
    def val(self, new_val):
        self._dlog("set(%s) = %d -> %d", 
                self._name, self._val, new_val)
        self._val = new_val
    def inc(self):
        self._val += 1
        self._dlog("inc(%s) -> %d", 
                self._name, self._val)
        return self._val
    def dec(self):
        self._val -= 1
        self._dlog("dec(%s) -> %d", 
                self._name, self._val)
        return self._val