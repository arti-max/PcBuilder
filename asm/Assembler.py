from Lexer import Lexer
from Parser import Parser
from Compiler import Compiler

class Assembler:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.compiler = Compiler()
    
    def assemble_file(self, filename, output_dir="boot"):
        """Ассемблирует файл и сохраняет результат"""
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        return self.assemble_string(source_code, output_dir)
    
    def assemble_string(self, source_code, output_dir="boot"):
        """Ассемблирует строку с кодом"""
        # Лексический анализ
        self.lexer = Lexer(source_code)
        tokens = self.lexer.tokenize()
        
        # Синтаксический анализ
        self.parser = Parser(tokens)
        statements = self.parser.parse()
        
        # Компиляция
        binary_data = self.compiler.compile(statements)
        
        # Сохранение
        self.compiler.save_to_files(binary_data, output_dir)
        self.compiler.save_to_tape(binary_data, "asm/tapes/tape.tape")
        
        return binary_data

def main():
    # Пример использования
    assembler = Assembler()
    
    test_code = """
#org 0x00ff
jmp main

main:
    mov A, 0 ; value
    mov D, 1 ; port
    call loop
    hlt

loop:
    out D, A
    cmp A, 0
    je .z
    sub A, D
    jmp loop
.z:
    add A, D
    jmp loop
    

"""
    
    try:
        #binary_data = assembler.assemble_string(test_code)
        #binary_data = assembler.assemble_file("asm/code/test_disp.asm")
        binary_data = assembler.assemble_file("asm/code/bios.asm")
        print(f"Ассемблирование завершено. Размер: {len(binary_data)} байт")
        print("Машинный код:", [hex(b) for b in binary_data])
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
