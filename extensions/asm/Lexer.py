import re
from enum import Enum

class TokenType(Enum):
    INSTRUCTION = "INSTRUCTION"
    REGISTER = "REGISTER"
    NUMBER = "NUMBER"
    LABEL = "LABEL"
    LOCAL_LABEL = "LOCAL_LABEL"
    IDENTIFIER = "IDENTIFIER"
    DIRECTIVE = "DIRECTIVE"
    COMMA = "COMMA"
    PLUS = "PLUS"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    SEMICOLON = "SEMICOLON"
    COMMENT = "COMMENT"
    NEWLINE = "NEWLINE"
    EOF = "EOF"

class Token:
    def __init__(self, type_, value, line=0, column=0):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Словарь для #define
        self.defines = {}
        
        self.instructions = {
            'nop', 'mov', 'ld', 'add', 'sub', 'xor', 'or', 'and', 'not',
            'cmp', 'jmp', 'je', 'jne', 'shl', 'shr', 'call', 'ret',
            'in', 'out', 'ldm', 'stm', 'stm_pair', 'hlt', 'push', 'pop', 'inc', 'dec'
        }
        
        self.registers = {'a', 'b', 'c', 'd', 'ip', 'ir', 'sp', 'bp', 'ss'}
        
        # Добавлена директива define (хотя она обрабатывается в препроцессоре)
        self.directives = {'org', 'db', 'define'}

    def current_char(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def peek_char(self, offset=1):
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]

    def advance(self):
        if self.pos < len(self.text) and self.text[self.pos] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1

    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t':
            self.advance()

    def read_number(self):
        result = ''
        # Hex number
        if self.current_char() == '0' and self.peek_char() and self.peek_char().lower() == 'x':
            self.advance()  # skip '0'
            self.advance()  # skip 'x'
            while self.current_char() and self.current_char().lower() in '0123456789abcdef':
                result += self.current_char()
                self.advance()
            return int(result, 16) if result else 0
        
        # Binary number
        if self.current_char() == '0' and self.peek_char() and self.peek_char().lower() == 'b':
            self.advance()  # skip '0'
            self.advance()  # skip 'b'
            while self.current_char() and self.current_char() in '01':
                result += self.current_char()
                self.advance()
            return int(result, 2) if result else 0
        
        # Decimal number
        while self.current_char() and self.current_char().isdigit():
            result += self.current_char()
            self.advance()
        return int(result) if result else 0

    def read_identifier(self):
        result = ''
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() in '_.')):
            result += self.current_char()
            self.advance()
        return result

    def read_comment(self):
        result = ''
        while self.current_char() and self.current_char() != '\n':
            result += self.current_char()
            self.advance()
        return result

    def preprocess_defines(self):
        """ИСПРАВЛЕННАЯ предварительная обработка #define директив"""
        lines = self.text.split('\n')
        processed_lines = []
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            stripped_line = line.strip()
            
            # Обработка #define
            if stripped_line.startswith('#define'):
                # ИСПРАВЛЕНИЕ 1: Разделяем по пробелам, но учитываем комментарии
                # Сначала убираем комментарии из строки
                comment_pos = stripped_line.find(';')
                if comment_pos != -1:
                    stripped_line = stripped_line[:comment_pos].strip()
                
                parts = stripped_line.split()
                if len(parts) >= 3:
                    # ИСПРАВЛЕНИЕ: #define NAME VALUE (только первые 3 части)
                    define_name = parts[1]
                    define_value = parts[2]  # ИСПРАВЛЕНО: берем только третий элемент
                    
                    # Пытаемся преобразовать в число
                    try:
                        # Hex
                        if define_value.startswith('0x') or define_value.startswith('0X'):
                            self.defines[define_name] = int(define_value, 16)
                        # Binary
                        elif define_value.startswith('0b') or define_value.startswith('0B'):
                            self.defines[define_name] = int(define_value, 2)
                        # Decimal
                        elif define_value.isdigit() or (define_value.startswith('-') and define_value[1:].isdigit()):
                            self.defines[define_name] = int(define_value)
                        else:
                            # Строковое значение или ссылка на другой define
                            self.defines[define_name] = define_value
                    except ValueError:
                        # Если не число - сохраняем как строку
                        self.defines[define_name] = define_value
                    
                    print(f"Define: {define_name} = {self.defines[define_name]}")
                    # Заменяем строку с #define на пустую
                    processed_lines.append('')
                else:
                    raise SyntaxError(f"Неверный синтаксис #define в строке {line_num}: {original_line}")
            else:
                # ИСПРАВЛЕНИЕ 2: Заменяем использования define'ов в обычных строках
                processed_line = line
                
                # Сортируем define'ы по длине имени (от длинных к коротким)
                # чтобы избежать частичных замен
                sorted_defines = sorted(self.defines.items(), key=lambda x: len(x[0]), reverse=True)
                
                for define_name, define_value in sorted_defines:
                    # ИСПРАВЛЕНИЕ: Используем word boundaries для точной замены
                    pattern = r'\b' + re.escape(define_name) + r'\b'
                    processed_line = re.sub(pattern, str(define_value), processed_line)
                
                processed_lines.append(processed_line)
        
        # ИСПРАВЛЕНИЕ 2: Обновляем текст после предобработки
        self.text = '\n'.join(processed_lines)
        print(f"После предобработки define'ов: {len(self.defines)} определений")

    def tokenize(self):
        # ИСПРАВЛЕНИЕ: Сначала обрабатываем #define
        self.preprocess_defines()
        
        # Сбрасываем позицию после предобработки
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        while self.pos < len(self.text):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            char = self.current_char()
            
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, char, self.line, self.column))
                self.advance()
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, char, self.line, self.column))
                self.advance()
            elif char == '+':
                self.tokens.append(Token(TokenType.PLUS, char, self.line, self.column))
                self.advance()
            elif char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, char, self.line, self.column))
                self.advance()
            elif char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, char, self.line, self.column))
                self.advance()
            elif char == ';':
                comment = self.read_comment()
                self.tokens.append(Token(TokenType.COMMENT, comment, self.line, self.column))
            elif char == '#':
                # Обработка директив (кроме #define, которые уже обработаны)
                self.advance()  # skip '#'
                directive = self.read_identifier()
                if directive.lower() in self.directives:
                    self.tokens.append(Token(TokenType.DIRECTIVE, directive.lower(), self.line, self.column))
                else:
                    raise SyntaxError(f"Неизвестная директива #{directive} в строке {self.line}")
            elif char.isdigit():
                number = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, number, self.line, self.column))
            elif char.isalpha() or char == '_' or char == '.':
                identifier = self.read_identifier()
                
                # Проверяем, заканчивается ли на двоеточие (метка)
                if self.current_char() == ':':
                    self.advance()  # skip ':'
                    if identifier.startswith('.'):
                        self.tokens.append(Token(TokenType.LOCAL_LABEL, identifier, self.line, self.column))
                    else:
                        self.tokens.append(Token(TokenType.LABEL, identifier, self.line, self.column))
                elif identifier.lower() in self.instructions:
                    self.tokens.append(Token(TokenType.INSTRUCTION, identifier.lower(), self.line, self.column))
                elif identifier.lower() in self.registers:
                    self.tokens.append(Token(TokenType.REGISTER, identifier.lower(), self.line, self.column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, identifier, self.line, self.column))
            else:
                raise SyntaxError(f"Неожиданный символ '{char}' в строке {self.line}, столбце {self.column}")
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def get_defines(self):
        """Возвращает словарь всех define'ов"""
        return self.defines.copy()
