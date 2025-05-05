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

_FRC_MAG = int(os.getenv('FRC_MAG')) # magnitude to more clearly render the fractal by making coordinates smaller (preferably < 2)
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
    
    # [HELPER] create a chunk
    def _GEN_0(self, IMG):
        SIZ_FIX = self.SIZ - ( self.SIZ / 2 )
        
        for Z in range(IMG.shape[0]):
            for X in range(IMG.shape[1]):
                for Y in range(IMG.shape[2]):
                    if Z % 0x10 == 0 and X % 0x10 == 0 and Y % 0x10 == 0: # test
                        IMG[Z, X, Y] = random.uniform(0.0, 1.0)
        
        return IMG
    
    # create a chunk
    def _GEN(self):
        # start with blank white
        IMG = np.full((self.SIZ, self.SIZ, self.SIZ), -1.0, dtype=np.int32)
        
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