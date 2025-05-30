from cpu.Alu import Alu
from cpu.Reg8 import Reg8
from cpu.Reg16 import Reg16
from cpu.ControlUnit import ControlUnit

import time

class Cpu:
    def __init__(self):
        self.name = "a8008 - 8bit cpu"
        self.registers = {
            0x01: Reg8(),   # A
            0x02: Reg8(),   # B
            0x03: Reg8(),   # C
            0x04: Reg8(),   # D
            0x05: Reg16(),  # IP (Instruction Pointer)
            0x06: Reg8(),   # IR (Instruction Register)
            0x07: Reg8(),   # SP (Stack Pointer)
            0x08: Reg8(),   # BP (Base Pointer)
            0x09: Reg8(),   # SS (Stack Segment)
        }
        self.flags = {
            0x01: Reg8(),  # Z (Zero)
            0x02: Reg8()   # C (Carry)
        }
        self.alu = Alu(self)
        self.control_unit = ControlUnit(self)
        self.ram = None
        self.running = False
    
    def set_ram(self, ram):
        self.ram = ram
    
    def set_device_manager(self, device_manager):
        self.device_manager = device_manager
        
    def _calculate_stack_address(self):
        ss = self.registers[0x09].read()  # Stack Segment
        sp = self.registers[0x07].read()  # Stack Pointer
        # 1 единица в SS = 256 байт (0x100)
        stack_base = ss * 0x100
        return stack_base + sp
    
    def fetch(self):
        ip = self.registers[0x05].read()
        instruction = self.ram.read(ip)
        self.registers[0x06].write(instruction)
        self.registers[0x05].write(ip + 1)
        
    def push(self, data):
        data = data & 0xFF
        
        # Сначала уменьшаем SP, затем записываем данные
        sp = self.registers[0x07].read()
        sp = (sp - 1) & 0xFF  # Уменьшаем SP с учетом 8-битного переполнения
        self.registers[0x07].write(sp)
        
        # Вычисляем физический адрес стека
        stack_address = self._calculate_stack_address()
        self.ram.write(stack_address, data)
        
        
    def pop(self):
        # Сначала читаем данные, затем увеличиваем SP
        stack_address = self._calculate_stack_address()
        data = self.ram.read(stack_address)
        
        sp = self.registers[0x07].read()
        sp = (sp + 1) & 0xFF  # Увеличиваем SP с учетом 8-битного переполнения
        self.registers[0x07].write(sp)
        
        return data
    
    def execute(self):
        opcode_name, _ = self.control_unit.decode()
        self.control_unit.execute(opcode_name)
    
    def run(self, start=0):
        self.registers[0x05].write(start)
        self.registers[0x09].write(0x00)  # SS = 0 (первый сегмент)
        self.registers[0x07].write(0xFF)  # SP = 0xFF (верх сегмента)
        self.running = True
        print(self.ram.memory[0x0107])
        
    def step(self):
        if self.running:
            self.fetch()
            self.execute()
            #time.sleep(1/740)
            
        # print(self.registers)
        # print(f"Flags - Z: {hex(self.flags[0x01].read())}, C: {hex(self.flags[0x02].read())}")
