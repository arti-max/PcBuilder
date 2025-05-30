; ========= DISPLAY DRIVER ==============

; draw_pix:
;     push bp
;     mov bp, sp

;     push a
;     push b
;     push c
;     push d

;     mov a, bp+3
;     mov a, [ss, a] ; x

;     mov b, bp+2
;     mov b, [ss, b] ; y

;     mov c, bp+1
;     mov c, [ss, c] ; state

;     mov d, 2 ; Display port
;     out d, a ; x
;     out d, b ; y
;     out d, c ; state

;     pop d
;     pop c
;     pop b
;     pop a

;     mov sp, bp
;     pop bp
;     ret


; Draw a pixel on screen
; A - x
; B - y
; C - on/off [1/0]
draw_pix:
    mov d, 2 ; Display port
    out d, a ; x
    out d, b ; y
    out d, c ; state
    ret