import random
import numpy as np
import cv2 # just to view noise map
import os
from dotenv import load_dotenv

load_dotenv()

_SED = int(np.clip(int(os.getenv('SED')), 0, (2 ** 32) - 1)) # random seed
_SIZ = int(os.getenv('SIZ')) # size of chunk
#_COL_DOT = np.clip(int(os.getenv('COL_DOT')), 1, 255) # color of dot setup for blur (lower color = higher effect)
#_MAG = int(os.getenv('MAG')) # number of times to soften chunk's noise
#_MAG_EDG = int(os.getenv('MAG_EDG')) # number of times to soften against other chunks' edges
#_WID_EDG = np.clip(int(os.getenv('WID_EDG')), 1, _SIZ // 2) # how thick chunk edges are considered to be
#_ALT_DEC = np.clip(int(os.getenv('ALT_DEC')), 1, 256) # flatten terrain (MAXIMUM ALTITUDE)
#_MAG_0   = int(os.getenv('MAG_0')) # extra magnitude constant

_FRC_MAG = int(os.getenv('FRC_MAG')) # magnitude to more clearly render the fractal by making coordinates smaller (preferably < 2)
_FRC_LOP_MAX = int(os.getenv('FRC_LOP_MAX')) # how many iterations to check if the function escapes 2 ; MUST BE UNDER UINT# DATA TYPE
_FRC_POW = float(os.getenv('FRC_POW')) # power for fractal function exponent
_FRC_COL_MAX = int(os.getenv('FRC_COL_MAX')) # 0 - X for voxel color gradient

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
        for Y in range(IMG.shape[0]):
            for X in range(IMG.shape[1]):
                for A in range(IMG.shape[2]):
                    '''
                    # Convert voxel coordinates to 3D space coordinates
                    x = ((self.SIZ * self.POS[0]) + X) / _FRC_MAG
                    y = ((self.SIZ * self.POS[1]) + Y) / _FRC_MAG
                    a = ((self.SIZ * self.POS[2]) + A) / _FRC_MAG
                    
                    # Initialize values for Mandelbulb calculation
                    zx, zy, zz = 0.0, 0.0, 0.0
                    FRC_ESC_YES = False
                    FRC_LOP_CNT = 0
                    
                    # Mandelbulb iteration
                    for I in range(_FRC_LOP_MAX):
                        # Calculate r (distance from origin)
                        r = np.sqrt(zx*zx + zy*zy + zz*zz)
                        
                        # Break if we exceed the bailout radius
                        if r > 2:
                            FRC_ESC_YES = True
                            FRC_LOP_CNT = I
                            break
                        
                        # Convert to spherical coordinates
                        if r < 1e-10:  # Avoid division by zero
                            theta = 0
                            phi = 0
                        else:
                            theta = np.arctan2(np.sqrt(zx*zx + zy*zy), zz)
                            phi = np.arctan2(zy, zx)
                        
                        # Apply power to spherical coordinates
                        r_pow = r ** _FRC_POW
                        theta_pow = theta * _FRC_POW
                        phi_pow = phi * _FRC_POW
                        
                        # Convert back to cartesian coordinates
                        sin_theta_pow = np.sin(theta_pow)
                        zx_new = r_pow * sin_theta_pow * np.cos(phi_pow)
                        zy_new = r_pow * sin_theta_pow * np.sin(phi_pow)
                        zz_new = r_pow * np.cos(theta_pow)
                        
                        # Add the original point (c value in the Mandelbulb formula)
                        zx = zx_new + x
                        zy = zy_new + y
                        zz = zz_new + a
                    
                    ESC = _FRC_COL_MAX + 1 # Default: empty voxel
                    
                    # If we escaped, calculate a value based on the iteration count
                    if FRC_ESC_YES:
                        ESC = int((FRC_LOP_CNT / _FRC_LOP_MAX) * _FRC_COL_MAX)

                    IMG[Y, X, A] = ESC
                    '''
                    #IMG[Y, X, A] = random.randint(0, _FRC_COL_MAX)
                    IMG[Y, X, A] = random.randint(0, 255)
        
        return IMG
    
    # create a chunk
    def _GEN(self):
        # start with blank white
        IMG = np.full((self.SIZ, self.SIZ, self.SIZ), _FRC_COL_MAX + 1, dtype=np.float32) # this data type is chosen for full rainbow gradient
        
        IMG = self._GEN_0(IMG)
        
        self.IMG = IMG
        
        '''cv2.imshow('IMG', IMG[:, :, 0])
        cv2.waitKey(0)
        cv2.destroyAllWindows()'''
        
        return IMG

_MAP = __MAP__()