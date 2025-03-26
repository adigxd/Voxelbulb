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
_MAG_EDG = int(os.getenv('MAG_EDG')) # number of times to soften against other chunk's edges
_WID_EDG = np.clip(int(os.getenv('WID_EDG')), 1, _SIZ // 2) # how thick edges are considered to be
_ALT_DEC = np.clip(int(os.getenv('ALT_DEC')), 1, 256) # flatten terrain

random.seed(_SED)
np.random.seed(_SED)

class __MAP__:
    def __init__(self):
        self.CHK_ARR = {}
    
    def _CHK_ADD(self, POS):
        CHK = __CHK__(POS, _SIZ)
        CHK._GEN()
        self.CHK_ARR[POS] = CHK.IMG

class __CHK__:
    def __init__(self, POS, SIZ=16):
        self.SIZ = SIZ
        self.POS = POS
        self.IMG = None
    
    # pixel within bounds?
    def _PXL_LOC_YES(self, Y, X):
        if (0 <= Y < self.SIZ) and (0 <= X < self.SIZ):
            return True
        else:
            return False
    
    # processed pixel's value before altitude reduction processing
    @staticmethod
    def _PXL_ACT(ALT):
        return np.clip((ALT / _ALT_DEC) * 255, 0, 255).astype(np.int32)
    
    # create a chunk
    def _GEN(self):
        # start with blank white
        IMG = np.full((self.SIZ, self.SIZ), 255, dtype=np.uint8)
        
        # temp image as processing may cause pixels' values to go over 255
        IMG_TMP = IMG.astype(np.int32)
        
        # blur setup (place dark 'dots')
        for Y in range(IMG_TMP.shape[0]):
            for X in range(IMG_TMP.shape[1]):
                if random.randint(0, 16) == 0:
                    IMG_TMP[Y, X] = _COL_DOT
                    
                    if self._PXL_LOC_YES(Y + 1, X): IMG_TMP[Y + 1, X] = _COL_DOT
                    if self._PXL_LOC_YES(Y - 1, X): IMG_TMP[Y - 1, X] = _COL_DOT
                    if self._PXL_LOC_YES(Y, X + 1): IMG_TMP[Y, X + 1] = _COL_DOT
                    if self._PXL_LOC_YES(Y, X - 1): IMG_TMP[Y, X - 1] = _COL_DOT
        
        # general blur (currently using 2 levels of adjacent pixels)
        for I in range(_MAG):
            for Y in range(IMG_TMP.shape[0]):
                for X in range(IMG_TMP.shape[1]):
                    PXL_NUM = 12 # number of pixels used to smooth
                    PXL_U2 = IMG_TMP[Y + 2, X] if self._PXL_LOC_YES(Y + 2, X) else IMG_TMP[Y, X]
                    PXL_U1 = IMG_TMP[Y + 1, X] if self._PXL_LOC_YES(Y + 1, X) else IMG_TMP[Y, X]
                    PXL_D2 = IMG_TMP[Y - 2, X] if self._PXL_LOC_YES(Y - 2, X) else IMG_TMP[Y, X]
                    PXL_D1 = IMG_TMP[Y - 1, X] if self._PXL_LOC_YES(Y - 1, X) else IMG_TMP[Y, X]
                    PXL_R2 = IMG_TMP[Y, X + 2] if self._PXL_LOC_YES(Y, X + 2) else IMG_TMP[Y, X]
                    PXL_R1 = IMG_TMP[Y, X + 1] if self._PXL_LOC_YES(Y, X + 1) else IMG_TMP[Y, X]
                    PXL_L2 = IMG_TMP[Y, X - 2] if self._PXL_LOC_YES(Y, X - 2) else IMG_TMP[Y, X]
                    PXL_L1 = IMG_TMP[Y, X - 1] if self._PXL_LOC_YES(Y, X - 1) else IMG_TMP[Y, X]
                    PXL_UR = IMG_TMP[Y + 1, X + 1] if self._PXL_LOC_YES(Y + 1, X + 1) else IMG_TMP[Y, X]
                    PXL_DR = IMG_TMP[Y - 1, X + 1] if self._PXL_LOC_YES(Y - 1, X + 1) else IMG_TMP[Y, X]
                    PXL_DL = IMG_TMP[Y - 1, X - 1] if self._PXL_LOC_YES(Y - 1, X - 1) else IMG_TMP[Y, X]
                    PXL_UL = IMG_TMP[Y + 1, X - 1] if self._PXL_LOC_YES(Y + 1, X - 1) else IMG_TMP[Y, X]
                    
                    # this is why we needed a temporary image
                    IMG_TMP[Y, X] = (PXL_U2 + PXL_U1 + PXL_D2 + PXL_D1 + PXL_R2 + PXL_R1 + PXL_L2 + PXL_L1 + PXL_UR + PXL_DR + PXL_DL + PXL_UL) // PXL_NUM
        
        # this chunk's position
        POS_Y, POS_X = self.POS
        
        # potential neighboring chunks (potential since some may not be rendered yet)
        POS_ARR = [(POS_Y - 1, POS_X), (POS_Y + 1, POS_X), (POS_Y, POS_X - 1), (POS_Y, POS_X + 1)]
        
        # index counter
        POS_IDX = 0
        
        # blurred image with sums to be divided by blur count for average
        IMG_TMP_NEW = np.full((self.SIZ, self.SIZ), 0, dtype=np.int32)
        
        # blur count (for end average)
        BLR_CNT = 0
        
        # neighbor chunk blurring (need to calulate all (potential) 4 neighboring chunks at once 
        # before applying the calculation, because if it were to be in sequence, 
        # the last chunks would have priority and somewhat override previous neighboring chunks' blurring; 
        # maybe only consider the neighbor's 1 width edge 'line' and mix depending on how close it is to that edge (closer = stronger) 
        # for each 1 width 'line' in current chunk parallel to that edge
        for POS in POS_ARR:
            if POS in _MAP.CHK_ARR:
                # get the other chunk if possible
                IMG_ALT = _MAP.CHK_ARR[POS]
                
                # for each edge, get the neighboring chunk's adjacent edge 
                #     (e.g. if doing current chunk's top edge, get top neighbor's bottom edge)
                # then, get that edge's pixel values prior processing and mix with edge (closer = higher weightage to edge & lower to self) 
                # to make chunk transitions smooth
                
                if POS_IDX == 0:
                    BLR_CNT += 1
                    
                    EDG_NEI = self._PXL_ACT(IMG_ALT[:1, :].flatten()) # bottom neighbor's top edge
                    
                    IMG_TMP_BLR = IMG_TMP
                    
                    for X in range(len(EDG_NEI)):
                        for Y in range(_SIZ):
                            PXL_CUR = IMG_TMP_BLR[Y, X]
                            PXL_NEI = EDG_NEI[X]
                            
                            IMG_TMP_BLR[Y, X] = ( ( PXL_CUR * (          Y   / _SIZ ) ) \
                                              +   ( PXL_NEI * ( ( _SIZ - Y ) / _SIZ ) ) )
                    
                    IMG_TMP_NEW += IMG_TMP_BLR
                
                elif POS_IDX == 1:
                    BLR_CNT += 1
                    
                    EDG_NEI = self._PXL_ACT(IMG_ALT[-1:, :].flatten()) # top neighbor's bottom edge
                    
                    IMG_TMP_BLR = IMG_TMP
                    
                    for X in range(len(EDG_NEI)):
                        for Y in range(_SIZ):
                            PXL_CUR = IMG_TMP_BLR[Y, X]
                            PXL_NEI = EDG_NEI[X]
                            
                            IMG_TMP_BLR[Y, X] = ( ( PXL_CUR * ( ( _SIZ - Y ) / _SIZ ) ) \
                                              +   ( PXL_NEI * (          Y   / _SIZ ) ) )
                    
                    IMG_TMP_NEW += IMG_TMP_BLR
                
                elif POS_IDX == 2:
                    BLR_CNT += 1
                    
                    EDG_NEI = self._PXL_ACT(IMG_ALT[:, -1:].flatten()) # left neighbor's right edge
                    
                    IMG_TMP_BLR = IMG_TMP
                    
                    for Y in range(len(EDG_NEI)):
                        for X in range(_SIZ):
                            PXL_CUR = IMG_TMP_BLR[Y, X]
                            PXL_NEI = EDG_NEI[Y]
                            
                            IMG_TMP_BLR[Y, X] = ( ( PXL_CUR * ( ( _SIZ - X ) / _SIZ ) ) \
                                              +   ( PXL_NEI * (          X   / _SIZ ) ) )
                    
                    IMG_TMP_NEW += IMG_TMP_BLR
                
                elif POS_IDX == 3:
                    BLR_CNT += 1
                    
                    EDG_NEI = self._PXL_ACT(IMG_ALT[:, :1].flatten()) # right neighbor's left edge
                    
                    IMG_TMP_BLR = IMG_TMP
                    
                    for Y in range(len(EDG_NEI)):
                        for X in range(_SIZ):
                            PXL_CUR = IMG_TMP_BLR[Y, X]
                            PXL_NEI = EDG_NEI[Y]
                            
                            IMG_TMP_BLR[Y, X] = ( ( PXL_CUR * (          X   / _SIZ ) ) \
                                              +   ( PXL_NEI * ( ( _SIZ - X ) / _SIZ ) ) )
                    
                    IMG_TMP_NEW += IMG_TMP_BLR
            
            POS_IDX += 1
        
        if BLR_CNT != 0:
            IMG_TMP_NEW //= BLR_CNT
        else:
            IMG_TMP_NEW = IMG_TMP
        
        # finalize
        IMG = np.clip(IMG_TMP_NEW, 0, 255).astype(np.uint8)
        
        for Y in range(IMG.shape[0]):
            for X in range(IMG.shape[1]):
                IMG[Y, X] = (IMG[Y, X] / 255) * _ALT_DEC
        
        self.IMG = IMG
        
        '''cv2.imshow('IMG', IMG)
        cv2.waitKey(0)
        cv2.destroyAllWindows()'''
        
        return IMG

_MAP = __MAP__()