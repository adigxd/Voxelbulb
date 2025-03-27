from map_1 import _MAP

from multiprocessing import Process, Queue
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time
import random
import numpy as np
import math
import os
from dotenv import load_dotenv

load_dotenv()

_THD_CNT   = np.clip(int(os.getenv('THD_CNT')), 1, os.cpu_count())
_TIC       = int(os.getenv('TIC'))
_CHK_TIC   = int(os.getenv('CHK_TIC'))
_FOV       = float(os.getenv('FOV'))
_SEE_MIN   = float(os.getenv('SEE_MIN'))
_SEE_MAX   = float(os.getenv('SEE_MAX'))
_SPD       = float(os.getenv('SPD'))
_SEN       = float(os.getenv('SEN'))
_SIZ       = int(os.getenv('SIZ'))
_LIN       = float(os.getenv('LIN'))
_DBG_SEE   = int(os.getenv('DBG_SEE'))
_PTH_SHA_V = os.getenv('PTH_SHA_V')
_PTH_SHA_F = os.getenv('PTH_SHA_F')
_COL_DEF   = tuple(map(float, os.getenv('COL_DEF').split(',')))
_COL_MIN   = tuple(map(float, os.getenv('COL_MIN').split(',')))
_COL_MAX   = tuple(map(float, os.getenv('COL_MAX').split(',')))
_ALT_MIN   = float(os.getenv('ALT_MIN'))
_CHK_DIS   = int(os.getenv('CHK_DIS'))
_ALT_DEC   = int(os.getenv('ALT_DEC'))

class Camera:
    def __init__(self, POS=[0, 0, 0], ROT=[0, 0]):
        self.pos = POS # x, ALT, z
        self.rot = ROT # pitch, yaw
        self.speed = _SPD
        self.sensitivity = _SEN

    def update(self, keys, mouse_rel):
        # Mouse look
        self.rot[0] -= mouse_rel[1] * self.sensitivity  # pitch
        self.rot[1] += mouse_rel[0] * self.sensitivity  # yaw
        
        # Clamp pitch to prevent flipping
        self.rot[0] = max(-89, min(89, self.rot[0]))
        
        # Calculate forward and right vectors
        yaw = math.radians(self.rot[1])
        pitch = math.radians(self.rot[0])
        
        forward = [
            math.sin(yaw),
            0,
            -math.cos(yaw)
        ]
        
        right = [
            math.cos(yaw),
            0,
            math.sin(yaw)
        ]
        
        # Movement
        if keys[pygame.K_w]:
            self.pos = [self.pos[i] + forward[i] * self.speed for i in range(3)]
        if keys[pygame.K_s]:
            self.pos = [self.pos[i] - forward[i] * self.speed for i in range(3)]
        if keys[pygame.K_a]:
            self.pos = [self.pos[i] - right[i] * self.speed for i in range(3)]
        if keys[pygame.K_d]:
            self.pos = [self.pos[i] + right[i] * self.speed for i in range(3)]
        if keys[pygame.K_SPACE]:
            self.pos[1] += self.speed
        if keys[pygame.K_LSHIFT]:
            self.pos[1] -= self.speed

    def look(self):
        # Clear transformation matrix
        glLoadIdentity()
        
        # Apply rotations first, then translation
        glRotatef(-self.rot[0], 1, 0, 0)
        glRotatef(-self.rot[1], 0, 1, 0)
        glTranslatef(-self.pos[0], -self.pos[1], -self.pos[2])



def _BUF(vertex_data, index_data):
    # Convert data to numpy arrays
    vertex_data = np.array(vertex_data, dtype=np.float32)
    index_data = np.array(index_data, dtype=np.uint32)

    # Generate and bind VAO
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Generate and bind VBO (Vertex Buffer Object)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    # Generate and bind EBO (Element Buffer Object)
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

    # Define vertex attribute pointer for positions (location=0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * vertex_data.itemsize, None) # last = ctypes.c_void_p(0) ?
    glEnableVertexAttribArray(0)

    # Unbind VAO to avoid accidental modification
    glBindVertexArray(0)

    return vao, vbo, ebo

def _REN(VAO, CNT_IDX, VBO, EBO):
    CNT_IDX = CNT_IDX * 3 # 3 per index idk
    glBindVertexArray(VAO)
    glDrawElements(GL_TRIANGLES, CNT_IDX, GL_UNSIGNED_INT, None)
    glBindVertexArray(0)

def _REN_DBG():
    # X
    glColor3f(*_COL_DEF)
    glBegin(GL_LINES)
    glVertex3f(-128, 0, 0)
    glVertex3f(128, 0, 0)
    glEnd()

    # Y
    glColor3f(*_COL_DEF)
    glBegin(GL_LINES)
    glVertex3f(0, -128, 0)
    glVertex3f(0, 128, 0)
    glEnd()

    # Z
    glColor3f(*_COL_DEF)
    glBegin(GL_LINES)
    glVertex3f(0, 0, -128)
    glVertex3f(0, 0, 128)
    glEnd()



def _SHA_GEN(PTH):
    try:
        with open(PTH, 'r') as F:
            SHA_SRC = F.read()
        return SHA_SRC
    except Exception as E:
        print(f'ERR >> _SHA_GEN >> cannot find {PTH}')
        return None

def _SHA_COM(SHA_SRC, SHA_TYP):
    SHA = glCreateShader(SHA_TYP)
    glShaderSource(SHA, SHA_SRC)
    glCompileShader(SHA)

    if not glGetShaderiv(SHA, GL_COMPILE_STATUS):
        ERR = glGetShaderInfoLog(SHA).decode()
        print(f'ERR >> _SHA_COM ({SHA_TYP}) >> {ERR}')
        return None

    return SHA

def _SHA_PRO(SHA_SRC_V, SHA_SRC_F):
    SHA_V = _SHA_COM(SHA_SRC_V, GL_VERTEX_SHADER)
    SHA_F = _SHA_COM(SHA_SRC_F, GL_FRAGMENT_SHADER)

    if SHA_V is None or SHA_F is None:
        # error message handled by shader compile function
        return None

    PRO_SHA = glCreateProgram()
    glAttachShader(PRO_SHA, SHA_V)
    glAttachShader(PRO_SHA, SHA_F)
    glLinkProgram(PRO_SHA)

    if not glGetProgramiv(PRO_SHA, GL_LINK_STATUS):
        glDeleteProgram(PRO_SHA)
        
        ERR = glGetProgramInfoLog(PRO_SHA).decode()
        print(f'ERR >> _SHA_PRO >> {ERR}')
        
        return None
    
    glDeleteShader(SHA_V)
    glDeleteShader(SHA_F)

    return PRO_SHA



def _UNI_MAT(PRO_SHA, MAT_M, MAT_V, MAT_P):
    LOC_M = glGetUniformLocation(PRO_SHA, 'model')
    LOC_V = glGetUniformLocation(PRO_SHA, 'view')
    LOC_P = glGetUniformLocation(PRO_SHA, 'projection')

    glUniformMatrix4fv(LOC_M, 1, GL_TRUE, MAT_M)
    glUniformMatrix4fv(LOC_V, 1, GL_TRUE, MAT_V)
    glUniformMatrix4fv(LOC_P, 1, GL_TRUE, MAT_P)

def _UNI_ETC(PRO_SHA, COL=_COL_DEF, COL_MIN=_COL_MIN, COL_MAX=_COL_MAX, SIZ=_SIZ, ALT_MIN=_ALT_MIN, ALT_MAX=_ALT_DEC):
    LOC_COL     = glGetUniformLocation(PRO_SHA, 'COL_DEF')
    LOC_COL_MIN = glGetUniformLocation(PRO_SHA, 'COL_MIN')
    LOC_COL_MAX = glGetUniformLocation(PRO_SHA, 'COL_MAX')
    LOC_SIZ     = glGetUniformLocation(PRO_SHA, 'SIZ')
    LOC_ALT_MIN = glGetUniformLocation(PRO_SHA, 'ALT_MIN')
    LOC_ALT_MAX = glGetUniformLocation(PRO_SHA, 'ALT_MAX')

    glUniform3fv(LOC_COL_MIN, 1, COL_MIN)
    glUniform3fv(LOC_COL_MAX, 1, COL_MAX)
    glUniform3fv(LOC_COL, 1, COL)
    glUniform1f(LOC_SIZ, SIZ)
    glUniform1f(LOC_ALT_MIN, ALT_MIN)
    glUniform1f(LOC_ALT_MAX, ALT_MAX)



def _GEN_MAT_M(POS=[0,0,0], ROT=[0,0,0], SCA=[1,1,1]):
    # Create 4x4 identity matrix filled with zeros except diagonal which is 1
    matrix = np.identity(4, dtype=np.float32)
    
    # Create translation matrix and set last column (except w) to position values
    translation = np.identity(4, dtype=np.float32)
    translation[0:3, 3] = POS  # Sets x,y,z translation in 4th column
    
    # Create 3 separate rotation matrices for x,y,z axes
    rot_x = np.identity(4, dtype=np.float32)
    rot_y = np.identity(4, dtype=np.float32)
    rot_z = np.identity(4, dtype=np.float32)
    
    # X rotation matrix - rotates around x axis
    rot_x[1,1] = np.cos(ROT[0])     # cos θ
    rot_x[1,2] = -np.sin(ROT[0])    # -sin θ
    rot_x[2,1] = np.sin(ROT[0])     # sin θ
    rot_x[2,2] = np.cos(ROT[0])     # cos θ
    
    # Y rotation matrix - rotates around y axis
    rot_y[0,0] = np.cos(ROT[1])     # cos θ
    rot_y[0,2] = np.sin(ROT[1])     # sin θ
    rot_y[2,0] = -np.sin(ROT[1])    # -sin θ
    rot_y[2,2] = np.cos(ROT[1])     # cos θ
    
    # Z rotation matrix - rotates around z axis
    rot_z[0,0] = np.cos(ROT[2])     # cos θ
    rot_z[0,1] = -np.sin(ROT[2])    # -sin θ
    rot_z[1,0] = np.sin(ROT[2])     # sin θ
    rot_z[1,1] = np.cos(ROT[2])     # cos θ
    
    # Scale matrix - stretches/shrinks along each axis
    scale = np.identity(4, dtype=np.float32)
    scale[0,0] = SCA[0]  # X scale
    scale[1,1] = SCA[1]  # Y scale
    scale[2,2] = SCA[2]  # Z scale
    
    # Combine all transforms in order: translate * rotX * rotY * rotZ * scale
    matrix = translation @ rot_x @ rot_y @ rot_z @ scale
    return matrix
    return gluPerspective(FOV, RES, DIS_MIN, DIS_MAX)

def _GEN_MAT_V(CAM_POS, CAM_ROT):
    # Convert camera rotation angles from degrees to radians
    pitch = np.radians(CAM_ROT[0])  # Up/down rotation
    yaw = np.radians(CAM_ROT[1])    # Left/right rotation
    
    # Calculate forward vector - where camera is looking
    forward = np.array([
        np.sin(yaw) * np.cos(pitch),   # X component
        np.sin(pitch),                  # Y component
        -np.cos(yaw) * np.cos(pitch)   # Z component
    ])
    
    # Calculate right vector using cross product of forward and world-up
    right = np.cross(forward, [0, 1, 0])
    right = right / np.linalg.norm(right)  # Normalize to unit length
    
    # Calculate camera's up vector using cross product of right and forward
    up = np.cross(right, forward)
    
    # Create rotation part of view matrix
    rotation = np.identity(4, dtype=np.float32)
    rotation[0, 0:3] = right     # First row is right vector
    rotation[1, 0:3] = up        # Second row is up vector
    rotation[2, 0:3] = -forward  # Third row is negative forward vector
    
    # Create translation matrix
    translation = np.identity(4, dtype=np.float32)
    translation[0:3, 3] = -np.array(CAM_POS)  # Negative camera position
    
    # Combine rotation and translation
    return rotation @ translation

def _GEN_MAT_P(FOV, ASPECT, NEAR, FAR):
    # Convert field of view from degrees to radians
    fov_rad = np.radians(FOV)
    
    # Calculate scaling factor based on FOV
    f = 1.0 / np.tan(fov_rad / 2.0)
    
    # Create empty 4x4 matrix
    matrix = np.zeros((4, 4), dtype=np.float32)
    
    # Set perspective transform values
    matrix[0,0] = f / ASPECT    # X scale (adjusted for aspect ratio)
    matrix[1,1] = f             # Y scale
    matrix[2,2] = (FAR + NEAR) / (NEAR - FAR)     # Z scale
    matrix[2,3] = (2.0 * FAR * NEAR) / (NEAR - FAR)  # Z translation
    matrix[3,2] = -1.0  # Set w coordinate for perspective divide
    
    return matrix



def _DIS(POS_A, POS_B):
    return math.sqrt((POS_A[0] - POS_B[0]) ** 2 + (POS_A[1] - POS_B[1]) ** 2)

_REQ_QUE = Queue()
_RES_QUE = Queue()
_THD_ARR = []
_VAO_ARR = {}

def _THD_FUN(REQ_QUE, RES_QUE):
    while True:
        REQ = REQ_QUE.get()
        
        if REQ is None: # sentinel value to stop thread
            break
        
        C_POS, SIZ = REQ
        
        _MAP._CHK_ADD(C_POS)
        CHK = _MAP.CHK_ARR[C_POS]
        
        GEN_VER_ARR = []
        GEN_IDX_ARR = []
        
        C_POS_ACT = (_SIZ * C_POS[0], _SIZ * C_POS[1])
        
        for Y in range(CHK.shape[0]):
            for X in range(CHK.shape[1]):
                for A in range(CHK[Y, X]):
                    # if not vertically exposed
                    if A != 0 and A != CHK[Y, X] - 1:
                        # if not on border of chunk
                        if (Y != 0 and Y != CHK.shape[0] - 1) and (X != 0 and X != CHK.shape[1] - 1):
                            # if completely surrounded
                            if A < CHK[Y - 1, X] and A < CHK[Y + 1, X] and A < CHK[Y, X - 1] and A < CHK[Y, X + 1]:
                                continue
                    
                    #SIZ_FIX = _SIZ // 2 # not good for infinite terrain gen
                    
                    X_FIX = X + C_POS_ACT[0] # - SIZ_FIX
                    Y_FIX = Y + C_POS_ACT[1] # - SIZ_FIX
                    
                    V_ARR = [
                        (X_FIX    , A    , Y_FIX    ), # 0
                        (X_FIX + 1, A    , Y_FIX    ), # 1
                        (X_FIX + 1, A    , Y_FIX + 1), # 2
                        (X_FIX    , A    , Y_FIX + 1), # 3
                        (X_FIX    , A + 1, Y_FIX    ), # 4
                        (X_FIX + 1, A + 1, Y_FIX    ), # 5
                        (X_FIX + 1, A + 1, Y_FIX + 1), # 6
                        (X_FIX    , A + 1, Y_FIX + 1)  # 7
                    ]

                    F_ARR = [
                        (0, 1, 2), (0, 2, 3), # D
                        (4, 5, 6), (4, 6, 7), # U
                        (0, 1, 5), (0, 5, 4), # F
                        (2, 3, 7), (2, 7, 6), # B
                        (0, 3, 7), (0, 7, 4), # L
                        (1, 2, 6), (1, 6, 5)  # R
                    ]

                    IDX = len(GEN_VER_ARR)    # Get the current length of the vertex array
                    GEN_VER_ARR.extend(V_ARR) # Add the vertices for this cube
                    GEN_IDX_ARR.extend([(V_A + IDX, V_B + IDX, V_C + IDX) for V_A, V_B, V_C in F_ARR])
        
        GEN_VER_ARR = np.array(GEN_VER_ARR, dtype=np.float32)
        GEN_IDX_ARR = np.array(GEN_IDX_ARR, dtype=np.uint32)
        
        print(f"[THD] Generated chunk @ {C_POS} ; putting in queue")
        
        RES_QUE.put((C_POS, GEN_VER_ARR, GEN_IDX_ARR))
        
        #REQ_QUE.task_done() # remove ?
        
        #time.sleep(0.01) # remove ?

def _THD_ARR_BEG():
    for _ in range(4):
        THD = Process(target=_THD_FUN, args=(_REQ_QUE, _RES_QUE), daemon=True)
        THD.start()
        _THD_ARR.append(THD)

def _THD_ARR_END():
    for _ in range(_THD_CNT): # sentinel value to stop thread
        _REQ_QUE.put(None)
    for THD in _THD_ARR:
        THD.terminate()
        #THD.join()
    _REQ_QUE.close() # added
    _RES_QUE.close() # added

def _GEN_MAP(POS, SIZ=_SIZ):
    CHK_LOW_X = int(POS[0] - _CHK_DIS)
    CHK_HIG_X = int(POS[0] + _CHK_DIS + 1)
    CHK_LOW_Y = int(POS[1] - _CHK_DIS)
    CHK_HIG_Y = int(POS[1] + _CHK_DIS + 1)
    
    REN_ARR = []
    
    for C_IDX_X in range(CHK_LOW_X, CHK_HIG_X):
        for C_IDX_Y in range(CHK_LOW_Y, CHK_HIG_Y):
            C_POS = (C_IDX_X, C_IDX_Y)
            
            DIS = _DIS(POS, C_POS)
            
            if DIS <= _CHK_DIS:
                REN_ARR.append((DIS, C_POS))
    
    REN_ARR.sort() # sorts by first item in tuple ; maybe also sort by chunks in front of camera: .sort(key=lambda C: (C[1], C[0]))
    
    for _, C_POS in REN_ARR:
        if C_POS not in _VAO_ARR:
            _REQ_QUE.put((C_POS, SIZ))
    
    ''' maybe reuse something like this later for other purposes
    REN_SET_REM = set(_VAO_ARR.keys()) - set(C[1] for C in REN_ARR)
    for C_POS in REN_SET_REM:
        VAO, _, VBO, EBO = _VAO_ARR[C_POS]
        
        glDeleteVertexArrays(1, [VAO])
        glDeleteBuffers(1, [VBO])
        glDeleteBuffers(1, [EBO])
        
        with _LCK_VAO_ARR: # remove lock ?
            del _VAO_ARR[C_POS]
    '''



def main():
    pygame.init()
    RES = (800, 600)
    pygame.display.set_mode(RES, DOUBLEBUF | OPENGL)
    pygame.display.set_caption('rndyz')
    IMG_WIN = pygame.image.load('./IMG_WIN-rndyz.png')
    pygame.display.set_icon(IMG_WIN)
    
    # Set up OpenGL
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    #glEnable(GL_CULL_FACE)
    #glCullFace(GL_BACK)
    glFrontFace(GL_CCW)
    glClearColor(*(map(lambda x: 0.5 * x, _COL_MIN)), 1)
    
    # Set up perspective
    glMatrixMode(GL_PROJECTION)
    gluPerspective(_FOV, (RES[0] / RES[1]), _SEE_MIN, _SEE_MAX)
    glMatrixMode(GL_MODELVIEW)
    
    # Initialize camera and mouse
    camera = Camera(POS=[0, _ALT_DEC, 0])
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    SHA_SRC_V = _SHA_GEN(f'{_PTH_SHA_V}')
    SHA_SRC_F = _SHA_GEN(f'{_PTH_SHA_F}')
    
    if SHA_SRC_V is None or SHA_SRC_F is None:
        exit()
    
    PRO_SHA = _SHA_PRO(SHA_SRC_V, SHA_SRC_F)
    if PRO_SHA is None:
        # error message handled by shader program function
        exit()
    
    glUseProgram(PRO_SHA)
    
    
    
    _THD_ARR_BEG()
    
    
    
    # Initialize matrices
    RES_RAT = RES[0] / RES[1]
    MAT_P = _GEN_MAT_P(_FOV, RES_RAT, _SEE_MIN, _SEE_MAX)
    MAT_M = _GEN_MAT_M()  # Use defaults for initial position
    
    glLineWidth(_LIN)
    
    clock = pygame.time.Clock()
    
    
    
    CHK_TIC_MAX = _CHK_TIC
    POS_PRE = (None, None)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_RSHIFT):
                _THD_ARR_END()
                
                glDeleteProgram(PRO_SHA)

                pygame.quit()

                return
        
        
        
        POS_CAM = (camera.pos[0], camera.pos[2])
        POS = (POS_CAM[0] // _SIZ, POS_CAM[1] // _SIZ)
        
        if POS_PRE != POS:
            POS_PRE = POS
            _GEN_MAP(POS_PRE, SIZ=_SIZ)
        
        
        
        CHK_TIC_CNT = 0
        
        while not _RES_QUE.empty() and CHK_TIC_CNT < CHK_TIC_MAX:
            try:
                C_POS, GEN_VER_ARR, GEN_IDX_ARR = _RES_QUE.get_nowait()
                
                T_A = time.perf_counter()
                VAO, VBO, EBO = _BUF(GEN_VER_ARR, GEN_IDX_ARR)
                _VAO_ARR[C_POS] = (VAO, len(GEN_IDX_ARR), VBO, EBO)
                T_B = time.perf_counter()
                print(f'[MAI] {T_B - T_A:.8f} s')
                
                CHK_TIC_CNT += 1
            except Exception:
                break
        
        
        
        # Get mouse movement
        mouse_rel = pygame.mouse.get_rel()
        keys = pygame.key.get_pressed()
        
        # Update camera
        camera.update(keys, mouse_rel)
        
        # Clear screen and reset matrix
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        MAT_V = _GEN_MAT_V(camera.pos, camera.rot)
        
        _UNI_MAT(PRO_SHA, MAT_M, MAT_V, MAT_P)
        
        _UNI_ETC(PRO_SHA, COL=_COL_DEF, COL_MIN=_COL_MIN, COL_MAX=_COL_MAX, SIZ=_SIZ, ALT_MIN=_ALT_MIN, ALT_MAX=_ALT_DEC)
        
        # Apply camera transformation
        camera.look()
        
        _REN_DBG()
        
        if _DBG_SEE != 0:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        
        
        
        CHK_LOW_X = int(POS[0] - _CHK_DIS)
        CHK_HIG_X = int(POS[0] + _CHK_DIS + 1)
        CHK_LOW_Y = int(POS[1] - _CHK_DIS)
        CHK_HIG_Y = int(POS[1] + _CHK_DIS + 1)
        
        for C_IDX_X in range(CHK_LOW_X, CHK_HIG_X):
            for C_IDX_Y in range(CHK_LOW_Y, CHK_HIG_Y):
                C_POS = (C_IDX_X, C_IDX_Y)
                
                if _DIS(POS, C_POS) > _CHK_DIS:
                    continue
                
                if C_POS in _VAO_ARR: # need ?
                    _REN(*_VAO_ARR[C_POS])
        
        
        
        if _DBG_SEE != 0:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        pygame.display.flip()
        clock.tick(_TIC)

if __name__ == '__main__':
    main()