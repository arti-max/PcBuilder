#org 0x0300
jmp main

; BIOS Device Ports
#define DISPLAY_PORT [0x0000]
#define KEYBOARD_PORT [0x0001]
#define BUZZER_PORT [0x0003]
#define TAPE_PORT [0x0002]
; DISPLAY
#define DISP_W 28
#define DISP_H 24
#define DISP_ON 1
#define DISP_OFF 0
; TAPE
#define SIGN_A 0xE7
#define SIGN_B 0xAA
; Other
#define TRUE 1
#define FALSE 0



main:
    xor a, a
    xor b, b
    xor c, c
    xor d, d
    mov sp, 0xff
    mov bp, 0xff
    mov ss, 0x00
    
    inc b
    mov a, DISPLAY_PORT
    out a, b
        
    hlt
    
    
#db 0xe7, 0xaa
   

    
   
