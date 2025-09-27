#version 330 core

layout (location = 0) in vec3 POS; // Vertex position attribute
layout (location = 1) in int FRC_ESC_IN_; // fractal color INC

//flat out int FRC_ESC_OUT; // fractal color OUT

flat out float Y; // to fragment shader
flat out float X; // to fragment shader
flat out float Z; // to fragment shader

uniform mat4 model;      // Model transformation
uniform mat4 view;       // Camera view transformation
uniform mat4 projection; // Perspective projection

void main()
{
    Y = floor(POS.y);
    X = floor(POS.x);
    Z = floor(POS.z);

    gl_Position = projection * view * model * vec4(POS, 1.0); // Transform vertex
	
	//FRC_ESC_OUT = FRC_ESC_IN_;
}
