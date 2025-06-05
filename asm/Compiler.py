import os
import json
import time
from datetime import datetime
from Parser import Instruction, Label, Directive, DataBytes

class TapeFormat:
    """Формат TAPE файла"""
    TAPE_SIZE = 2048  # 2KB максимальный размер
    HEADER_SIZE = 128  # Размер заголовка
    
    @staticmethod
    def create_tape_file(data, metadata):
        """Создает TAPE файл с заголовком и данными"""
        # Создаем заголовок
        header = bytearray(TapeFormat.HEADER_SIZE)
        
        # Магическое число для идентификации TAPE файла
        header[0:4] = b'TAPE'
        
        # Версия формата
        header[4] = 1
        header[5] = 0
        
        # Размер данных (2 байта)
        data_size = len(data)
        header[6] = (data_size >> 8) & 0xFF
        header[7] = data_size & 0xFF
        
        # Время создания (4 байта Unix timestamp)
        timestamp = int(time.time())
        header[8] = (timestamp >> 24) & 0xFF
        header[9] = (timestamp >> 16) & 0xFF
        header[10] = (timestamp >> 8) & 0xFF
        header[11] = timestamp & 0xFF
        
        # Название кассеты (32 байта)
        name = metadata.get('name', 'Untitled')[:31]
        name_bytes = name.encode('utf-8')
        header[12:12+len(name_bytes)] = name_bytes
        
        # Автор (32 байта)
        author = metadata.get('author', 'Unknown')[:31]
        author_bytes = author.encode('utf-8')
        header[44:44+len(author_bytes)] = author_bytes
        
        # Описание (32 байта)
        description = metadata.get('description', '')[:31]
        desc_bytes = description.encode('utf-8')
        header[76:76+len(desc_bytes)] = desc_bytes
        
        # Контрольная сумма заголовка
        checksum = sum(header[:-4]) & 0xFFFF
        header[124] = (checksum >> 8) & 0xFF
        header[125] = checksum & 0xFF
        
        # Создаем полный файл
        tape_data = bytearray(TapeFormat.TAPE_SIZE)
        tape_data[:TapeFormat.HEADER_SIZE] = header
        
        # Копируем данные программы
        data_start = TapeFormat.HEADER_SIZE
        if len(data) > TapeFormat.TAPE_SIZE - TapeFormat.HEADER_SIZE:
            raise ValueError(f"Программа слишком большая: {len(data)} байт, максимум {TapeFormat.TAPE_SIZE - TapeFormat.HEADER_SIZE}")
        
        tape_data[data_start:data_start+len(data)] = data
        
        # Остальное место заполняется нулями (NOP)
        return tape_data
    
    @staticmethod
    def read_tape_file(tape_data):
        """Читает TAPE файл и возвращает заголовок и данные"""
        if len(tape_data) < TapeFormat.HEADER_SIZE:
            raise ValueError("Неверный размер TAPE файла")
        
        header = tape_data[:TapeFormat.HEADER_SIZE]
        
        # Проверяем магическое число
        if header[0:4] != b'TAPE':
            raise ValueError("Не является TAPE файлом")
        
        # Извлекаем информацию из заголовка
        version = (header[4], header[5])
        data_size = (header[6] << 8) | header[7]
        timestamp = (header[8] << 24) | (header[9] << 16) | (header[10] << 8) | header[11]
        
        name = header[12:44].decode('utf-8').rstrip('\x00')
        author = header[44:76].decode('utf-8').rstrip('\x00')
        description = header[76:108].decode('utf-8').rstrip('\x00')
        
        # Проверяем контрольную сумму
        stored_checksum = (header[124] << 8) | header[125]
        calculated_checksum = sum(header[:-4]) & 0xFFFF
        
        if stored_checksum != calculated_checksum:
            print("Предупреждение: Неверная контрольная сумма заголовка")
        
        metadata = {
            'version': version,
            'data_size': data_size,
            'timestamp': timestamp,
            'creation_date': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'name': name,
            'author': author,
            'description': description
        }
        
        # Извлекаем данные программы
        data_start = TapeFormat.HEADER_SIZE
        program_data = tape_data[data_start:data_start+data_size] if data_size > 0 else bytearray()
        
        return metadata, program_data

class Compiler:
    def __init__(self):
        self.opcodes = {
            'nop': 0x00,
            'mov': 0x01,
            'ld': 0x02,
            'add': 0x03,
            'sub': 0x04,
            'xor': 0x05,
            'or': 0x06,
            'and': 0x07,
            'not': 0x08,
            'cmp': 0x09,
            'jmp': 0x0A,
            'je': 0x0B,
            'jne': 0x0C,
            'shl': 0x0D,
            'shr': 0x0E,
            'call': 0x0F,
            'ret': 0x10,
            'in': 0x11,
            'out': 0x12,
            'ldm': 0x13,
            'ldm_r_pair': 0x14,
            'push': 0x15,
            'pop': 0x16,
            'inc': 0x17,
            'dec': 0x18,
            'stm': 0x19,
            'stm_pair': 0x1A,
            'hlt': 0xFF
        }
        
        self.labels = {}
        self.binary_data = []
        self.current_address = 0
        self.org_address = 0
        self.physical_address = 0
    
    def first_pass(self, statements):
        logical_address = self.org_address
        physical_address = 0
        
        for statement in statements:
            if isinstance(statement, Directive):
                if statement.name == 'org':
                    logical_address = statement.value
                    self.org_address = statement.value
            elif isinstance(statement, Label):
                self.labels[statement.name] = logical_address
            elif isinstance(statement, Instruction):
                instruction_size = self.get_instruction_size(statement)
                logical_address += instruction_size
                physical_address += instruction_size
            elif isinstance(statement, DataBytes):
                # НОВОЕ: обработка #db директивы
                logical_address += len(statement.data)
                physical_address += len(statement.data)
    
    def get_instruction_size(self, instruction):
        opcode = instruction.opcode
        
        if opcode == 'nop' or opcode == 'ret' or opcode == 'hlt':
            return 1
        elif opcode in ['shl', 'shr', 'push', 'pop', 'inc', 'dec']:
            return 2
        elif opcode in ['add', 'sub', 'xor', 'or', 'and', 'not', 'jmp', 'je', 'jne', 'call', 'in', 'out']:
            return 3
        elif opcode in ['mov', 'ld', 'cmp', 'ldm', 'stm', 'stm_pair']:
            return 4
        else:
            return 1
    
    def compile_operand(self, operand):
        if not operand:
            return []
        
        op_type, *args = operand
        
        if op_type == 'register':
            return [args[0]]
        elif op_type == 'immediate':
            return [args[0] & 0xFF]
        elif op_type == 'register_offset':
            return [args[0], args[1] & 0xFF]
        elif op_type == 'memory_direct':
            addr = args[0]
            return [(addr >> 8) & 0xFF, addr & 0xFF]
        elif op_type == 'memory_pair':
            return [args[0], args[1]]
        elif op_type == 'label_ref':
            if args[0] in self.labels:
                addr = self.labels[args[0]]
                return [(addr >> 8) & 0xFF, addr & 0xFF]
            else:
                raise ValueError(f"Неизвестная метка: {args[0]}")
        
        return []
    
    def compile_instruction(self, instruction):
        opcode = instruction.opcode
        operands = instruction.operands
        
        # [Вся логика компиляции инструкций остается такой же, как в предыдущем коде]
        if opcode == 'cmp' and len(operands) == 2:
            first_op, second_op = operands
            
            if first_op[0] == 'register' and second_op[0] == 'register':
                mode = 0x00
                return [self.opcodes['cmp'], first_op[1], second_op[1], mode]
            elif first_op[0] == 'register' and second_op[0] == 'immediate':
                mode = 0x01
                return [self.opcodes['cmp'], first_op[1], second_op[1], mode]
            elif first_op[0] == 'immediate' and second_op[0] == 'register':
                mode = 0x02
                return [self.opcodes['cmp'], first_op[1], second_op[1], mode]
            elif first_op[0] == 'immediate' and second_op[0] == 'immediate':
                mode = 0x03
                return [self.opcodes['cmp'], first_op[1], second_op[1], mode]
            else:
                raise ValueError(f"Неподдерживаемые типы операндов для CMP: {first_op[0]}, {second_op[0]}")
        
        elif opcode == 'mov' and len(operands) == 2:
            dest, src = operands
            
            if dest[0] == 'memory_pair' and src[0] == 'register':
                return [self.opcodes['stm_pair'], dest[1], dest[2], src[1]]
            elif dest[0] == 'memory_direct' and src[0] == 'register':
                addr_bytes = self.compile_operand(dest)
                return [self.opcodes['stm']] + addr_bytes + [src[1]]
            elif dest[0] == 'label_ref' and src[0] == 'register':
                addr_bytes = self.compile_operand(dest)
                return [self.opcodes['stm']] + addr_bytes + [src[1]]
            elif src[0] == 'immediate':
                return [self.opcodes['ld'], dest[1], src[1], 0x00]
            elif src[0] == 'memory_pair':
                return [self.opcodes['ldm_r_pair'], dest[1], src[1], src[2]]
            elif src[0] == 'memory_direct':
                addr_bytes = self.compile_operand(src)
                return [self.opcodes['ldm'], dest[1]] + addr_bytes
            elif src[0] == 'label_ref':
                addr_bytes = self.compile_operand(src)
                return [self.opcodes['ldm'], dest[1]] + addr_bytes
            else:
                result = [self.opcodes['mov']]
                result.append(dest[1])
                result.append(src[1])
                if src[0] == 'register_offset':
                    result.append(src[2])
                else:
                    result.append(0x00)
                return result
        
        elif opcode == 'stm' and len(operands) == 2:
            addr_op, reg_op = operands
            
            if addr_op[0] == 'memory_direct' and reg_op[0] == 'register':
                addr_bytes = self.compile_operand(addr_op)
                return [self.opcodes['stm']] + addr_bytes + [reg_op[1]]
            elif addr_op[0] == 'label_ref' and reg_op[0] == 'register':
                addr_bytes = self.compile_operand(addr_op)
                return [self.opcodes['stm']] + addr_bytes + [reg_op[1]]
            else:
                raise ValueError(f"Неподдерживаемые операнды для STM: {addr_op[0]}, {reg_op[0]}")
        
        elif opcode == 'stm_pair' and len(operands) == 3:
            high_reg, low_reg, data_reg = operands
            
            if (high_reg[0] == 'register' and low_reg[0] == 'register' and data_reg[0] == 'register'):
                return [self.opcodes['stm_pair'], high_reg[1], low_reg[1], data_reg[1]]
            else:
                raise ValueError(f"STM_PAIR требует три регистра: {high_reg[0]}, {low_reg[0]}, {data_reg[0]}")
        
        result = [self.opcodes[opcode]]
        
        for operand in operands:
            result.extend(self.compile_operand(operand))
        
        target_size = self.get_instruction_size(instruction)
        while len(result) < target_size:
            result.append(0x00)
        
        return result
    
    def second_pass(self, statements):
        self.physical_address = 0
        
        for statement in statements:
            if isinstance(statement, Instruction):
                bytes_data = self.compile_instruction(statement)
                self.binary_data.extend(bytes_data)
                self.physical_address += len(bytes_data)
            elif isinstance(statement, DataBytes):
                # НОВОЕ: добавляем сырые байты из #db
                self.binary_data.extend(statement.data)
                self.physical_address += len(statement.data)
            elif isinstance(statement, Directive):
                pass
    
    def compile(self, statements):
        self.first_pass(statements)
        self.second_pass(statements)
        return self.binary_data
    
    def save_to_tape(self, binary_data, output_path, metadata=None):
        """НОВОЕ: Сохраняет в TAPE файл"""
        if metadata is None:
            metadata = {
                'name': os.path.splitext(os.path.basename(output_path))[0],
                'author': 'PC Builder',
                'description': 'Assembled program'
            }
        
        tape_data = TapeFormat.create_tape_file(binary_data, metadata)
        
        with open(output_path, 'wb') as f:
            f.write(tape_data)
        
        print(f"TAPE файл создан: {output_path}")
        print(f"Размер программы: {len(binary_data)} байт")
        print(f"Размер TAPE: {len(tape_data)} байт")
        print(f"Название: {metadata['name']}")
        
        return tape_data
    
    def save_to_files(self, binary_data, output_dir="boot"):
        """Сохраняет бинарные данные в файлы (для загрузки в ОЗУ)"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if len(binary_data) <= 256:
            with open(os.path.join(output_dir, "0.bin"), "wb") as f:
                f.write(bytes(binary_data))
            print(f"Создан файл 0.bin размером {len(binary_data)} байт")
        elif len(binary_data) <= 512:
            with open(os.path.join(output_dir, "0.bin"), "wb") as f:
                f.write(bytes(binary_data[:256]))
            with open(os.path.join(output_dir, "1.bin"), "wb") as f:
                f.write(bytes(binary_data[256:]))
            print(f"Создан файл 0.bin размером 256 байт")
            print(f"Создан файл 1.bin размером {len(binary_data) - 256} байт")
        else:
            raise ValueError("Программа слишком большая (больше 512 байт)")
    
    def get_load_address(self):
        return self.org_address
