#org 0x300
    
main:
    xor a, a
    xor b, b
    xor c, c
    xor d, d
    mov sp, 0xff
    mov bp, 0xff
    xor ss, ss
    
    call main_logic
    
    hlt
    
    
main_logic:
    mov a, [0x0000]    ; Display PORT to A
    