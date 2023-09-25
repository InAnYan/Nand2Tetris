// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.


// Not the best approach, but easy to implement.

(LOOP)

@KBD
D=M

@WHITE
D; JEQ

(BLACK)

@i
M=0

(BLACK_FILL)

@i
D=M
@R16
M=D
@8192
D=A
@R16
D=D-M
@LOOP
D; JEQ

@SCREEN
D=A
@i
A=D+M
M=-1

@i
M=M+1

@BLACK_FILL
0; JEQ

(WHITE)

@i
M=0

(WHITE_FILL)

@i
D=M
@R16
M=D
@8192
D=A
@R16
D=D-M
@LOOP
D; JEQ

@SCREEN
D=A
@i
A=D+M
M=0

@i
M=M+1

@WHITE_FILL
0; JEQ
