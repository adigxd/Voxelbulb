#version 330 core

out vec4 FragColor; // Output color

flat in float Y; // from vertex shader
flat in float X; // from vertex shader
flat in float Z; // from vertex shader

flat in float FRC_COL;

uniform vec3 COL_DEF; // Custom uniform for coloring

uniform vec3 COL_MIN;
uniform vec3 COL_MAX;

uniform float SIZ;

vec3 __COL(float COL)
{
	float RAT = COL;
	
	if(RAT <= 0.200) { return mix(vec3(1.0, 0.0, 0.0), vec3(1.0, 1.0, 0.0), 5 * (RAT - 0.000)); }
	if(RAT <= 0.400) { return mix(vec3(1.0, 1.0, 0.0), vec3(0.0, 1.0, 0.0), 5 * (RAT - 0.200)); }
	if(RAT <= 0.600) { return mix(vec3(0.0, 1.0, 0.0), vec3(0.0, 1.0, 1.0), 5 * (RAT - 0.400)); }
	if(RAT <= 0.800) { return mix(vec3(0.0, 1.0, 1.0), vec3(0.0, 0.0, 1.0), 5 * (RAT - 0.600)); }
	if(RAT <= 1.000) { return mix(vec3(0.0, 0.0, 1.0), vec3(1.0, 0.0, 1.0), 5 * (RAT - 0.800)); }
	else             { return vec3(1.0, 1.0, 1.0); } // this should never happen
}

void main()
{
    vec3 COL = __COL(FRC_COL);

    FragColor = vec4(COL, 1.0);
}
