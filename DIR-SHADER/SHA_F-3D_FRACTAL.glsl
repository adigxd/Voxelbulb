#version 330 core

out vec4 FragColor; // Output color

flat in float Y; // from vertex shader
flat in float X; // from vertex shader
flat in float Z; // from vertex shader

in float FRC_COL;

uniform vec3 COL_DEF; // Custom uniform for coloring

uniform vec3 COL_MIN;
uniform vec3 COL_MAX;

uniform float SIZ;

vec3 __COL(float RAT)
{
    float RAT_MAX_0 = 0.200;
    float RAT_MAX_1 = 0.400;
    float RAT_MAX_2 = 0.600;
    float RAT_MAX_3 = 0.800;
    float RAT_MAX_4 = 1.000;
    
	if(RAT <= RAT_MAX_0) { return mix(vec3(1.0, 0.0, 0.0), vec3(1.0, 1.0, 0.0), 5 * RAT); }
	if(RAT <= RAT_MAX_1) { return mix(vec3(1.0, 1.0, 0.0), vec3(0.0, 1.0, 0.0), 5 * (RAT - RAT_MAX_0)); }
	if(RAT <= RAT_MAX_2) { return mix(vec3(0.0, 1.0, 0.0), vec3(0.0, 1.0, 1.0), 5 * (RAT - RAT_MAX_1)); }
	if(RAT <= RAT_MAX_3) { return mix(vec3(0.0, 1.0, 1.0), vec3(0.0, 0.0, 1.0), 5 * (RAT - RAT_MAX_2)); }
	if(RAT <= RAT_MAX_4) { return mix(vec3(0.0, 0.0, 1.0), vec3(1.0, 0.0, 1.0), 5 * (RAT - RAT_MAX_3)); }
	else                 { return vec3(1.0, 1.0, 1.0); } // this should never happen
}

void main()
{
    vec3 COL = __COL(FRC_COL);

    FragColor = vec4(COL, 1.0);
}
