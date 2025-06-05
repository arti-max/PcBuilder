from Lexer import TokenType, Token

class Instruction:
    def __init__(self, opcode, operands=None):
        self.opcode = opcode
        self.operands = operands or []

class Label:
    def __init__(self, name):
        self.name = name

class Directive:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class DataBytes:
    def __init__(self, data):
        self.data = data  # Список байтов

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
        self.current_label_context = None
        
        self.register_map = {
            'a': 0x01, 'b': 0x02, 'c': 0x03, 'd': 0x04,
            'ip': 0x05, 'ir': 0x06, 'sp': 0x07, 'bp': 0x08, 'ss': 0x09
        }

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def skip_newlines(self):
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()

    def expect(self, token_type):
        if not self.current_token or self.current_token.type != token_type:
            raise SyntaxError(f"Ожидался {token_type}, получен {self.current_token}")
        token = self.current_token
        self.advance()
        return token

    def resolve_label_name(self, label_name):
        """Преобразует локальную метку в полное имя"""
        if label_name.startswith('.') and self.current_label_context:
            return f"{self.current_label_context}{label_name}"
        return label_name

    def parse_directive(self):
        """Парсит директиву"""
        if not self.current_token or self.current_token.type != TokenType.DIRECTIVE:
            return None

        directive_name = self.current_token.value
        self.advance()

        if directive_name == 'org':
            if self.current_token and self.current_token.type == TokenType.NUMBER:
                address = self.current_token.value
                self.advance()
                return Directive('org', address)
            else:
                raise SyntaxError("Ожидался адрес после директивы #org")

        elif directive_name == 'db':
            # Обработка директивы #db
            data_bytes = []
            if self.current_token and self.current_token.type == TokenType.NUMBER:
                data_bytes.append(self.current_token.value & 0xFF)
                self.advance()
                
                # Парсим остальные байты через запятую
                while self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()  # skip ','
                    if self.current_token and self.current_token.type == TokenType.NUMBER:
                        data_bytes.append(self.current_token.value & 0xFF)
                        self.advance()
                    else:
                        raise SyntaxError("Ожидался байт после запятой в #db")
                
                return DataBytes(data_bytes)
            else:
                raise SyntaxError("Ожидались байты после директивы #db")

        # УДАЛЕНО: Обработка #define (теперь в препроцессоре)
        
        return None

    # Остальные методы остаются без изменений...
    def parse_operand(self):
        if not self.current_token:
            return None

        if self.current_token.type == TokenType.REGISTER:
            reg = self.current_token.value
            self.advance()
            
            if self.current_token and self.current_token.type == TokenType.PLUS:
                self.advance()
                if self.current_token and self.current_token.type == TokenType.NUMBER:
                    offset = self.current_token.value
                    self.advance()
                    return ('register_offset', self.register_map[reg], offset)
                else:
                    raise SyntaxError("Ожидалось число после '+'")
            
            return ('register', self.register_map[reg])

        elif self.current_token.type == TokenType.NUMBER:
            number = self.current_token.value
            self.advance()
            return ('immediate', number)

        elif self.current_token.type == TokenType.LBRACKET:
            self.advance()  # skip '['
            
            if self.current_token.type == TokenType.REGISTER:
                first_reg = self.current_token.value
                self.advance()
                
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()  # skip ','
                    if self.current_token.type == TokenType.REGISTER:
                        second_reg = self.current_token.value
                        self.advance()
                        self.expect(TokenType.RBRACKET)
                        return ('memory_pair', self.register_map[first_reg], self.register_map[second_reg])
                    else:
                        raise SyntaxError("Ожидался второй регистр в [reg, reg]")
                else:
                    self.expect(TokenType.RBRACKET)
                    return ('memory_reg', self.register_map[first_reg])
                    
            elif self.current_token.type == TokenType.NUMBER:
                address = self.current_token.value
                self.advance()
                self.expect(TokenType.RBRACKET)
                return ('memory_direct', address)
            else:
                raise SyntaxError("Неожиданный операнд в скобках")

        elif self.current_token.type == TokenType.IDENTIFIER:
            label_name = self.current_token.value
            resolved_name = self.resolve_label_name(label_name)
            self.advance()
            return ('label_ref', resolved_name)

        else:
            raise SyntaxError(f"Неожиданный операнд: {self.current_token}")

    def parse_instruction(self):
        if not self.current_token or self.current_token.type != TokenType.INSTRUCTION:
            return None

        opcode = self.current_token.value
        self.advance()

        operands = []
        if self.current_token and self.current_token.type not in [TokenType.NEWLINE, TokenType.COMMENT, TokenType.EOF]:
            operands.append(self.parse_operand())
            
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()  # skip ','
                operands.append(self.parse_operand())

        return Instruction(opcode, operands)

    def parse(self):
        statements = []
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            self.skip_newlines()
            
            if not self.current_token or self.current_token.type == TokenType.EOF:
                break

            if self.current_token.type == TokenType.DIRECTIVE:
                directive = self.parse_directive()
                if directive:
                    statements.append(directive)

            elif self.current_token.type == TokenType.LABEL:
                label_name = self.current_token.value
                self.current_label_context = label_name
                statements.append(Label(label_name))
                self.advance()

            elif self.current_token.type == TokenType.LOCAL_LABEL:
                local_name = self.current_token.value
                if self.current_label_context:
                    full_name = f"{self.current_label_context}{local_name}"
                    statements.append(Label(full_name))
                else:
                    statements.append(Label(local_name))
                self.advance()

            elif self.current_token.type == TokenType.INSTRUCTION:
                instruction = self.parse_instruction()
                if instruction:
                    statements.append(instruction)

            elif self.current_token.type == TokenType.COMMENT:
                self.advance()

            else:
                raise SyntaxError(f"Неожиданный токен: {self.current_token}")

        return statements
