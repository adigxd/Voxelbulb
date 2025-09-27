#version 330 core

out vec4 FragColor; // Output color

flat in float Y; // from vertex shader
flat in float X; // from vertex shader
flat in float Z; // from vertex shader

in float FRC_COL;
in vec3 POS_SHA_F;
in vec3 NML;

uniform vec3 COL_DEF; // Custom uniform for coloring

uniform vec3 COL_MIN;
uniform vec3 COL_MAX;

uniform float SIZ;

uniform vec3 LIT_POS;
uniform vec3 LIT_COL;
uniform float LIT_INT;
uniform float LIT_RAD;

vec3 __COL(float RAT)
{
	// return vec3(0.5, 0.5, 0.5); // testing
	
    float RAT_MAX_0 = 0.200;
    float RAT_MAX_1 = 0.400;
    float RAT_MAX_2 = 0.600;
    float RAT_MAX_3 = 0.800;
    float RAT_MAX_4 = 1.000;
    
	vec3 COL_R = vec3(0.0, 0.0, 0.0);
	vec3 COL_Y = vec3(0.17, 0.17, 0.17);
	vec3 COL_G = vec3(0.33, 0.33, 0.33);
	vec3 COL_C = vec3(0.5, 0.5, 0.5);
	vec3 COL_B = vec3(0.67, 0.67, 0.67);
	vec3 COL_M = vec3(0.83, 0.83, 0.83);
	
	if(RAT <= RAT_MAX_0) { return mix(COL_R, COL_Y, 5 * RAT); }
	if(RAT <= RAT_MAX_1) { return mix(COL_Y, COL_G, 5 * (RAT - RAT_MAX_0)); }
	if(RAT <= RAT_MAX_2) { return mix(COL_G, COL_C, 5 * (RAT - RAT_MAX_1)); }
	if(RAT <= RAT_MAX_3) { return mix(COL_C, COL_B, 5 * (RAT - RAT_MAX_2)); }
	if(RAT <= RAT_MAX_4) { return mix(COL_B, COL_M, 5 * (RAT - RAT_MAX_3)); }
	else                 { return vec3(1.0, 1.0, 1.0); } // this should never happen
}

void main()
{
    vec3 COL = __COL(FRC_COL);
	COL = mix(COL, vec3(1.0, 1.0, 1.0), 0.9); // brighten it up a bit before lighting
	
	
	// STEP 1: LIGHT DIRECTION AND DISTANCE
	
	vec3 LIT_DIR = LIT_POS - POS_SHA_F; // direction from pixel to light
	float LIT_DIS = length(LIT_DIR); // distance magnitude
	LIT_DIR = normalize(LIT_DIR); // magnitude of 1
	
	
	// STEP 2: ATTENUATION (LIGHT FALLOFF)
	
	float LIT_ATN = LIT_INT / (1.0 + LIT_DIS * LIT_DIS * 0.0001); // last number is arbitrary; inverse relationship with world position scale
	LIT_ATN *= 1.0 - clamp(LIT_DIS / LIT_RAD, 0.0, 1.0); // without this, light would never be 0 (just approaches it); but when distance > light radius here, it ensures 0
	
	
	// STEP 3: DIFFUSE LIGHTING (SURFACE ANGLE)
	
	float LIT_DIF = max(dot(NML, LIT_DIR), 0.0); // less brightness if it's coming at an angle to surface
	
	
	// STEP 4: AMBIENT LIGHTING
	
	float LIT_AMB = 0.125; // hard-coded so every surface gets at least 25% brightness to prevent full black
	
	
	// STEP 5: COMBINE
	
	vec3 LIT = (LIT_AMB + LIT_DIF * LIT_ATN) * LIT_COL;
	vec3 COL_PST = COL * LIT; // post-lighting
	
	
    FragColor = vec4(COL_PST, 1.0);
}
