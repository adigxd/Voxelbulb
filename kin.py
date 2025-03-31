import os
import numpy as np
import math
from dotenv import load_dotenv

load_dotenv()

_SPD     = max(0, float(os.getenv('SPD')))
_ACC_D   = min(0, float(os.getenv('ACC_D')))
_GLD_MAG = min(1, float(os.getenv('GLD_MAG'))) # gliding while holding shift
_JMP_MAG = max(0, float(os.getenv('JMP_MAG')))

class __KIN__:
    def __init__(self, OFF, POS):
        self.OFF = OFF # camera height offset
        self.POS = POS # (X, Y, Z)
        self.VEL = [0, 0, 0]
        self.ACC = [0, 0, 0]
        self.ALT_MIN = 0
    
    '''
    ALT_MIN = height of current block directly under player
    ''' 
    def _UPD(self, ALT_MIN, JMP_YES=False, GLD_YES=False):
        self.ALT_MIN = ALT_MIN
        
        if self.POS[1] - self.OFF == self.ALT_MIN and JMP_YES:
            self.VEL[2] = math.sqrt(-2 * _JMP_MAG * _ACC_D)
        
        if self.VEL[2] < 0 and self.POS[1] - self.OFF <= self.ALT_MIN:
            self.VEL[2] = 0
        
        if self.POS[1] - self.OFF > self.ALT_MIN:
            ACC_D_FIX = _ACC_D * _GLD_MAG if GLD_YES else _ACC_D
            
            self.VEL[2] += ACC_D_FIX