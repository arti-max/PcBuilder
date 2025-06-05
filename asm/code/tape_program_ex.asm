#org 0x0300
jmp main

main:
    ; clear registers
    xor a, a
    xor b, b
    xor c, c
    xor d, d
    mov sp, 0xFF
    mov bp, 0xFF
    mov ss, 0x00

    ; program
    mov a, 0xEE

    hlt
