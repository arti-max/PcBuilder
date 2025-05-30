#org 0x00ff
jmp main

; ========= DISPLAY DRIVER ==============

draw_pix:
    ; Параметры уже в регистрах A, B, C
    mov d, 2 ; Display port
    out d, a ; x
    out d, b ; y  
    out d, c ; state
    ret

; ====== MAIN ======

main:
    mov d, 1
    mov a, 0 ; x
    mov b, 0 ; y
    call loop
    hlt

loop:
    mov c, 1    ; state = включен
    call draw_pix
    
    add a, c    ; x++
    cmp a, 16   ; сравниваем с 16 (0x10)
    jne .continue
    
    ; Переход на новую строку
    mov a, 0    ; x = 0
    add b, c    ; y++
    cmp b, 16   ; сравниваем с 16
    jne .continue
    
    ; Конец - все пиксели нарисованы
    ret
    
.continue:
    jmp loop