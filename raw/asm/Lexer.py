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
        
        self.instructions = {
            'nop', 'mov', 'ld', 'add', 'sub', 'xor', 'or', 'and', 'not',
            'cmp', 'jmp', 'je', 'jne', 'shl', 'shr', 'call', 'ret',
            'in', 'out', 'ldm', 'stm', 'stm_pair', 'hlt', 'push', 'pop', 'inc', 'dec'
        }
        
        self.registers = {'a', 'b', 'c', 'd', 'ip', 'ir', 'sp', 'bp', 'ss'}
        
        # ДОБАВЛЕНА директива db
        self.directives = {'org', 'db'}
    
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
    
    def tokenize(self):
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
                # Обработка директив
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
