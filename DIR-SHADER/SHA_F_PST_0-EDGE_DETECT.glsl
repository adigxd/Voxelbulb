#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D TXT;
uniform vec2 RES;

float __FLT_RAN(vec2 co)
{
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main()
{
	vec4 COL = texture(TXT, TexCoord);
	
	float VAL = dot(COL.rgb, vec3(0.333, 0.333, 0.333));
	
	float FLT_RAN = __FLT_RAN(TexCoord * RES); // multiple by RES to ensure randomness
	
	if(FLT_RAN < VAL) { FragColor = vec4(vec3(1.0), 1.0); }
	else			  { FragColor = vec4(vec3(0.0), 1.0); }
}