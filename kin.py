import os
import math
from dotenv import load_dotenv

load_dotenv()

_SPD = os.getenv('SPD')
_ACC_D = -0.004
_JMP_MAG = 4

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
    def _UPD(self, ALT_MIN, JMP_YES=False):
        self.ALT_MIN = ALT_MIN
        
        if self.POS[1] - self.OFF == self.ALT_MIN and JMP_YES:
            print('JUMPING')
            self.VEL[2] = math.sqrt(-2 * _JMP_MAG * _ACC_D)
        
        if self.VEL[2] < 0 and self.POS[1] - self.OFF <= self.ALT_MIN:
            self.VEL[2] = 0
        
        if self.POS[1] - self.OFF > self.ALT_MIN:
            print('GRAVITY')
            self.VEL[2] += _ACC_D