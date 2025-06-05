#org 0x00ff
jmp main

; ОПТИМИЗИРОВАННЫЙ поиск устройств
; A=порт, B=серийный_номер -> D=ошибка, A=порт
__find_device:
    push c
    xor c, c
.loop:
    inc c
    out c, b        ; отправляем серийный номер
    in c, a         ; читаем ответ
    cmp a, b        ; сравниваем
    je .found
    cmp c, 5        ; проверяем лимит портов
    jne .loop
    mov d, 1        ; ошибка
    mov a, b        ; возвращаем серийный номер
    jmp .exit
.found:
    xor d, d        ; успех
    mov a, c        ; возвращаем порт
.exit:
    pop c
    ret

main:
    ; Поиск зуммера
    mov b, 0x2f
    call __find_device
    cmp d, 1
    je .fail_silent
    mov [0x0003], a

    ; Поиск дисплея  
    mov b, 0x4f
    call __find_device
    cmp d, 1
    mov b, 0x03
    je .fail_beep
    mov [0x0000], a

    ; Поиск клавиатуры
    mov b, 0x4e
    call __find_device
    cmp d, 1
    mov b, 0x04
    je .fail_beep
    mov [0x0001], a

    ; Поиск кассеты
    mov b, 0x7a
    call __find_device
    cmp d, 1
    mov b, 0x05
    je .fail_beep
    mov [0x0002], a

    ; Загрузочный звук
    mov a, [0x0003]
    mov b, 0x01
    out a, b

    ; Загрузка программы
    mov d, 0x03
    call __load_program
    
    jmp 0x0300

.fail_silent:
    hlt

; B - err code
.fail_beep:
    mov a, [0x0003]
    out a, b
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
    ; check tape
    push d
    call __check_tape
    cmp d, 0x00
    pop d
    je __load_program
    ; load byte
    in a, b
    ; c is overflow?
    cmp b, 0xE7
    je .signature
    ; store byte to ram
    mov [d, c], b
    ; increment c
    inc c
    ; is overflow?
    cmp c, 0xff
    je .upgrade
    ; go to loop
    jmp .loop
    
    
.signature:
    push d ; save mem bank
    push b ; save 0xE7
    
    in a, d
    
    cmp d, 0xAA
    je .sign_end
    mov a, d
    
    pop b
    pop d
    
    mov [d, c], b
    ; increment c
    inc c
    ; is overflow?
    cmp c, 0xff
    mov b, a
    mov a, [0x0002]
    je .upgrade_sign
    
    jmp .loop
    
.sign_end:
    pop b
    pop d
    jmp .end
    
.upgrade_sign:
    inc d
    xor c, c
    
    mov [d, c], b
    jmp .loop
    
.upgrade:
    inc d
    xor c, c
    jmp .loop

.end:
    ret
