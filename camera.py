#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 13:26:46 2017

@author: lessig
"""

import numpy as np
import ray
"""
 Coordinate system 
 Z goes into the picture
 
           +Z
   -X    .
   ^    . 
   .   . 
   .  . 
   . . 
   ..........> +Y


"""


class Camera :

    def __init__( self, res_x = 512, res_y = 512):
        self.pos = [0, 0, -10]
        # todo maybe implement proper camera orientation
        #self.viewdir = np.array( [0.0, 0.0,0.0])
        #self.updir = np.array( [0.0, -1.0, 0.0])
        self.fov = (30.0 * np.pi) / 180.0
        self.flength = 1.0
        self.image = np.zeros( (res_x, res_y, 3), dtype=np.float)
    
    def generateRay( self, pix_x, pix_y) :
        
        # compute direction
        xmax = np.sin( self.fov) * self.flength
        dx = -xmax + pix_x * (2 * xmax) / (self.image.shape[0])
        dy = -xmax + pix_y * (2 * xmax) / (self.image.shape[1])
        
        dir = np.array([dx, dy, 1.0])
        dir = dir / np.linalg.norm( dir)
        
        r = ray.Ray( self.pos, dir)
        return r
    