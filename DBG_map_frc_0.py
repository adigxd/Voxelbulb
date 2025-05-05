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
        """
        Calculate whether a 3D point is in the mandelbulb set
        Returns a value between 0.0 and 1.0 for points in the set (didn't escape)
        Returns -1.0 for points that escaped (these won't be rendered)
        """
        # Scale coordinates based on the fractal magnitude
        scale = _FRC_MAG
        x0, y0, z0 = x/scale, y/scale, z/scale
        
        # Center the mandelbulb in the chunk
        #x0 -= self.SIZ / (2 * scale)
        #y0 -= self.SIZ / (2 * scale)
        #z0 -= self.SIZ / (2 * scale)
        
        # Initialize variables
        n = _FRC_POW  # Power for the mandelbulb
        cx, cy, cz = x0, y0, z0  # Original coordinates
        x, y, z = 0, 0, 0  # Current position
        
        # Iterate to determine if point is in mandelbulb set
        iteration = 0
        for iteration in range(_FRC_LOP_MAX):
            # Calculate radius
            r = np.sqrt(x*x + y*y + z*z)
            
            #if x0 == 0 and y0 == 0 and z0 == 0:
            #    print(f'<!> {r}')
            
            # Check if point escapes
            if r > 2.0:
                # Point escaped, don't render it
                return -1.0
                
            #if r < 1e-10:  # Avoid division by zero <- COMMENTING THIS OUT FIXES (?)
            #    break
                
            # Convert to spherical coordinates
            theta = np.arctan2(np.sqrt(x*x + y*y), z)
            phi = np.arctan2(y, x)
            
            # Apply power formula
            r_n = r**n
            x = r_n * np.sin(theta * n) * np.cos(phi * n) + cx
            y = r_n * np.sin(theta * n) * np.sin(phi * n) + cy
            z = r_n * np.cos(theta * n) + cz
            
        # Return value for non-escaping points (in the set)
        if iteration == _FRC_LOP_MAX - 1:
            #if x0 == 0 and y0 == 0 and z0 == 0:
            #    print('<!> ORIGIN DID NOT ESCAPE')
            # Point didn't escape (in the set) - render it with a value of 1.0
            return 1.0
        else:
            # Point didn't reach the maximum iteration but also didn't escape
            # Colorize based on how close it was to escaping
            return -1.0#(iteration / _FRC_LOP_MAX)
    
    # [HELPER] create a chunk
    def _GEN_0(self, IMG):
        # Generate mandelbulb values for each voxel in the chunk
        for z in range(IMG.shape[0]):
            for x in range(IMG.shape[1]):
                for y in range(IMG.shape[2]):
                    world_x = self.POS[0] * self.SIZ + x
                    world_y = self.POS[1] * self.SIZ + y
                    world_z = self.POS[2] * self.SIZ + z
                    
                    value = self._mandelbulb(world_x, world_y, world_z)
                    
                    # Store the value in the image array
                    IMG[z, x, y] = value
        
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