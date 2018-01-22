#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 13:58:48 2017

@author: lessig
"""

import numpy as np
from Shapes.shape import Shape
import time

class Sphere( Shape) :
    intersectTimeSec = 0
    intersectCount = 0

    def __init__(self, pos, r, color) :
    
        super().__init__(color)
        
        self.pos = pos
        self.r = r
        self.tri = False    #no triangle

    def intersect(self, ray):
        Sphere.intersectCount += 1
        t0 = time.process_time()
        val = self.auxIntersect(ray)
        Sphere.intersectTimeSec += time.process_time() - t0
        return val

    def auxIntersect(self, ray):
        
        # compute intersection point with sphere
        q = ray.o - self.pos
        
        c = np.dot( q, q) - (self.r * self.r)
        b = 2.0 * np.dot( q, ray.d)
        
        temp = b*b - 4*c 
        if( temp < 0.0) :
            return False
        
        temp = np.sqrt( temp)
        s1 = 1.0/2.0 * ( -b + temp) 
        s2 = 1.0/2.0 * ( -b - temp)
        
        sol = s1
        if s1 < 0.0 and s2 < 0.0:
            return False
        if s1 < 0.0:
            sol = s2
        elif s2 < 0.0 : 
            sol = s1
        elif s2 < s1 :
            sol = s2
            
        if sol < ray.t :
            ray.t = sol;
            return True
            
        return False
        
        
    