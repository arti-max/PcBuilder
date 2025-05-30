#org 0x00ff
jmp main

; A - buzzer port  
; D - is Err
__fbp:
    push c
    xor c, c    ; port

.loop:
    inc c
    mov a, 0x2f
    out c, a
    in c, a

    cmp a, 0x2f ; buzzer serial number
    je .end
    cmp c, 5
    je .fail
    jmp .loop
.end:
    mov d, 0 ; no fail
    mov a, c
    pop c
    ret
.fail:
    mov d, 1 ; fail
    mov a, 0x2f
    pop c
    ret

; A - display port
; D - is Errr
__fdp16:
    push c
    xor c, c    ; port

.loop:
    inc c
    mov a, 0x4f
    out c, a
    in c, a

    cmp a, 0x4f ; display 16x16 serial number
    je .end
    cmp c, 5
    je .fail
    jmp .loop
.end:
    mov d, 0 ; no fail
    mov a, c
    pop c
    ret
.fail:
    mov d, 1 ; fail
    mov a, 0x4f
    pop c
    ret

; A - tape loader port
; D - is Err
__ftlp:
    push c
    xor c, c    ; port

.loop:
    inc c
    mov a, 0x7a
    out c, a
    in c, a

    cmp a, 0x7a ; tape loader serial number
    je .end
    cmp c, 5
    je .fail
    jmp .loop
.end:
    mov d, 0 ; no fail
    mov a, c
    pop c
    ret
.fail:
    mov d, 1 ; fail
    mov a, 0x7a
    pop c
    ret

; A - Keyboard port
; D - is Err
__fkp:
    push c
    xor c, c    ; port
.loop:
    inc c
    mov a, 0x4e
    out c, a
    in c, a

    cmp a, 0x4e ; keyboard serial number
    je .end
    cmp c, 5
    je .fail
    jmp .loop
.end:
    mov d, 0 ; no fail
    mov a, c
    pop c
    ret
.fail:
    mov d, 1 ; fail
    mov a, 0x4e
    pop c
    ret

main:
    ; check buzzer
    call __fbp
    cmp d, 1
    je .fail_boot_silent
    mov [0x0003], a ; BUZZER port
    ; check display
    call __fdp16
    cmp d, 1
    je .fail_display
    mov [0x0000], a ; DISP port
    ; check keyboard
    call __fkp
    cmp d, 1
    je .fail_keyboard
    mov [0x0001], a ; KBRD port
    ; check tape lodaer
    call __ftlp
    cmp d, 1
    je .fail_tape
    mov [0x0002], a ; TLDR port

    mov a, [0x0003]
    mov b, 0x01
    call __beep_error

    mov a, [0x0002]
    xor a, a

    mov d, 0x03 ; arg 1
    call __load_program
    jmp 0x0300

.fail_boot_silent:
    hlt

.fail_display:
    mov a, [0x0003] ; Buzzer port
    mov b, 0x03     ; Display error pattern
    call __beep_error
    jmp .loop

.fail_keyboard:
    mov a, [0x0003] ; Buzzer port  
    mov b, 0x04     ; Keyboard error pattern
    call __beep_error
    jmp .loop

.fail_tape:
    mov a, [0x0003] ; Buzzer port
    mov b, 0x05     ; Tape error pattern  
    call __beep_error
    jmp .loop

.loop:
    jmp .loop

; Stop proccess, while tape is not loaded
__wait_for_tape: 
    push d
    push a 
.loop:
    call __check_tape
    cmp d, 0x01
    je .end
    jmp .loop
.end:
    pop a
    pop d
    ret

; Returns: D - exists Tape
__check_tape:
    push a
    mov d, 0x06
    out a, d
    in a, d
    pop a
    ret

; Load program from TAPE
; D - start memory bank
__load_program:
    ; 0xE7 - end program signature
    xor c, c    ; loww addr byte
    xor b, b
    mov a, [0x0002] ; TL port

    call __wait_for_tape

    mov b, 0x01 ; Rewind
    out a, b
    mov b, 0x02 ; Play
    out a, b

.loop:
    push d
    call __check_tape
    cmp d, 0x00
    je __load_program
    pop d
    in a, b
    cmp b, 0xE7
    je .end
    mov [d, c], b

    inc c
    cmp c, 0xff
    je .upgrade

    jmp .loop

.upgrade:
    inc d
    xor c, c
    jmp .loop

.end:
    ret


; A - buzzer port
; B - error song
__beep_error:
    out a, b
    ret