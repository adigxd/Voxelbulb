import random
import numpy as np
import cv2 # just to view noise map
import os
from dotenv import load_dotenv

load_dotenv()

MAG = int(os.getenv('MAG')) # number of times to soften noise

class Map:
    def __init__(self, SIZ=16):
        self.SIZ = SIZ

    def _PXL(self, Y, X):
        if (0 <= Y < self.SIZ) and (0 <= X < self.SIZ):
            return True
        else:
            return False

    def _MAP(self):
        IMG = np.random.randint(0, 255, (self.SIZ, self.SIZ), dtype=np.uint8)

        IMG_TMP = IMG.astype(np.int32)

        PXL_IDX_ARR = []
        for Y in range(self.SIZ):
            for X in range(self.SIZ):
                PXL_IDX_ARR.append((Y, X))
        random.shuffle(PXL_IDX_ARR)

        for I in range(MAG):
            for Y in range(IMG_TMP.shape[0]):
                for X in range(IMG_TMP.shape[1]):
                    PXL_NUM = 12 # number of pixels used to smooth
                    PXL_U2 = IMG_TMP[Y + 2, X] if self._PXL(Y + 2, X) else IMG_TMP[Y, X]
                    PXL_U1 = IMG_TMP[Y + 1, X] if self._PXL(Y + 1, X) else IMG_TMP[Y, X]
                    PXL_D2 = IMG_TMP[Y - 2, X] if self._PXL(Y - 2, X) else IMG_TMP[Y, X]
                    PXL_D1 = IMG_TMP[Y - 1, X] if self._PXL(Y - 1, X) else IMG_TMP[Y, X]
                    PXL_R2 = IMG_TMP[Y, X + 2] if self._PXL(Y, X + 2) else IMG_TMP[Y, X]
                    PXL_R1 = IMG_TMP[Y, X + 1] if self._PXL(Y, X + 1) else IMG_TMP[Y, X]
                    PXL_L2 = IMG_TMP[Y, X - 2] if self._PXL(Y, X - 2) else IMG_TMP[Y, X]
                    PXL_L1 = IMG_TMP[Y, X - 1] if self._PXL(Y, X - 1) else IMG_TMP[Y, X]
                    PXL_UR = IMG_TMP[Y + 1, X + 1] if self._PXL(Y + 1, X + 1) else IMG_TMP[Y, X]
                    PXL_DR = IMG_TMP[Y - 1, X + 1] if self._PXL(Y - 1, X + 1) else IMG_TMP[Y, X]
                    PXL_DL = IMG_TMP[Y - 1, X - 1] if self._PXL(Y - 1, X - 1) else IMG_TMP[Y, X]
                    PXL_UL = IMG_TMP[Y + 1, X - 1] if self._PXL(Y + 1, X - 1) else IMG_TMP[Y, X]

                    IMG_TMP[Y, X] = (PXL_U2 + PXL_U1 + PXL_D2 + PXL_D1 + PXL_R2 + PXL_R1 + PXL_L2 + PXL_L1 + PXL_UR + PXL_DR + PXL_DL + PXL_UL) // PXL_NUM

        IMG = np.clip(IMG_TMP, 0, 255).astype(np.uint8)

        MIN = IMG.min()
        IMG = IMG - MIN

        return IMG