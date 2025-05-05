import random
import numpy as np
import cv2 # just to view noise map
import os
from dotenv import load_dotenv

load_dotenv()

_SED = int(np.clip(int(os.getenv('SED')), 0, (2 ** 32) - 1)) # random seed
_SIZ = int(os.getenv('SIZ')) # size of chunk
_COL_DOT = np.clip(int(os.getenv('COL_DOT')), 1, 255) # color of dot setup for blur (lower color = higher effect)
_MAG = int(os.getenv('MAG')) # number of times to soften chunk's noise
_MAG_EDG = int(os.getenv('MAG_EDG')) # number of times to soften against other chunks' edges
_WID_EDG = np.clip(int(os.getenv('WID_EDG')), 1, _SIZ // 2) # how thick chunk edges are considered to be
_ALT_DEC = np.clip(int(os.getenv('ALT_DEC')), 1, 256) # flatten terrain (MAXIMUM ALTITUDE)
_MAG_0   = int(os.getenv('MAG_0')) # extra magnitude constant

_FRC_MOD = int(os.getenv('FRC_MOD')) # fractal mode (0 for normal, 1 for inverted 'alpha')
_FRC_MAG = float(os.getenv('FRC_MAG')) # magnitude to more clearly render the fractal by making coordinates smaller (preferably < 2)
_FRC_LOP_MAX = int(os.getenv('FRC_LOP_MAX')) # how many iterations to check if the function escapes 2
_FRC_POW = float(os.getenv('FRC_POW')) # power for fractal function exponent

random.seed(_SED)
np.random.seed(_SED)

class __MAP__:
    def __init__(self):
        self.CHK_ARR = {}
    
    def _CHK_ADD(self, POS):
        CHK = __CHK__(POS, _SIZ)
        CHK._GEN()
        self.CHK_ARR[POS] = CHK.IMG
    
    def _CHK_ADD_MAN(self, POS, CHK_IMG): # manual chunk add
        self.CHK_ARR[POS] = CHK_IMG

class __CHK__:
    def __init__(self, POS, SIZ=16):
        self.SIZ = SIZ
        self.POS = POS
        self.IMG = None
    
    def _mandelbulb(self, x, y, z):
        scale = _FRC_MAG
        x0, y0, z0 = x/scale, y/scale, z/scale
        
        n = _FRC_POW  # Power for the mandelbulb
        cx, cy, cz = x0, y0, z0  # Original coordinates
        x, y, z = 0, 0, 0  # Current position
        
        R_END = 0
        
        for I in range(_FRC_LOP_MAX):
            r = np.sqrt(x*x + y*y + z*z)
            
            if r > 2.0:
                if _FRC_MOD == 0:
                    return -1.0
                
                return I / _FRC_LOP_MAX
            
            theta = np.arctan2(np.sqrt(x*x + y*y), z)
            phi = np.arctan2(y, x)
            
            r_n = r**n
            x = r_n * np.sin(theta * n) * np.cos(phi * n) + cx
            y = r_n * np.sin(theta * n) * np.sin(phi * n) + cy
            z = r_n * np.cos(theta * n) + cz
            
            R_END = r
        
        if _FRC_MOD == 0:
            return R_END / 2.0
        
        return -1.0
        
    
    # [HELPER] create a chunk
    def _GEN_0(self, IMG):
        # Generate mandelbulb values for each voxel in the chunk
        for Z in range(IMG.shape[0]):
            for X in range(IMG.shape[1]):
                for Y in range(IMG.shape[2]):
                    X_FIX = self.POS[0] * self.SIZ + X
                    Y_FIX = self.POS[1] * self.SIZ + Y
                    Z_FIX = self.POS[2] * self.SIZ + Z
                    
                    if X_FIX > 2.0 or Y_FIX > 2.0 or Z_FIX > 2.0:
                        IMG[Z, X, Y] = -1.0
                    
                    IMG[Z, X, Y] = self._mandelbulb(X_FIX, Y_FIX, Z_FIX)
        
        return IMG
    
    # create a chunk
    def _GEN(self):
        # start with blank white
        IMG = np.full((self.SIZ, self.SIZ, self.SIZ), -1.0, dtype=np.float32)  # Changed to float32 for more precision
        
        IMG = self._GEN_0(IMG)
        
        '''for Y in range(IMG.shape[0]):
            for X in range(IMG.shape[1]):
                IMG[Y, X] = (IMG[Y, X] / 255) * _ALT_DEC'''
        
        self.IMG = IMG
        
        '''cv2.imshow('IMG', IMG)
        cv2.waitKey(0)
        cv2.destroyAllWindows()'''
        
        return IMG

_MAP = __MAP__()