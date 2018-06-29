# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 13:00:18 2017

@author: jhills
"""

import math
import csv

stop_val = 1000000
curr_val = 1

primes = []
RESULT = []
pcnt = 0

while (curr_val < stop_val):
    curr_val += 1
    c = curr_val
    factors = []
    is_prime = 0
    
    for p in primes[:]:
        
        if pow(p,2) > c:                        # No more to check 
            break
        
        while (c > 1):                          # Divide out this prime    
            d, m = divmod(c, p)
            if m: break
            c = d
            factors.append(p)
            
    if c > 1:
        if c == curr_val:                       # New prime      
            primes.append(curr_val)
            pcnt += 1
            factors.append(curr_val)
            is_prime = 1
        else:                                   # Factor we already know
            prev_result = RESULT[c - 2]
            factors.extend(prev_result[5:])
    
    fcnt = len(factors)
    
    factors.insert(0, fcnt)                     # Number of Factors
    factors.insert(0, curr_val - primes[-1])    # Distance from last prime
    factors.insert(0, pcnt)                     # Prime index (if prime)
    factors.insert(0, is_prime)                 # Prime categorization
    factors.insert(0, curr_val)                 # Value
    
    RESULT.append(factors)
    if (curr_val%10000 == 0):
        print ('complete: ' + str(curr_val) + '\tpcnt: ' + str(pcnt))
    
with open('primes.data.csv', "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n", delimiter=',')
        writer.writerows(RESULT)
        csv_file.close