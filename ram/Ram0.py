class Ram0:
    def __init__(self):
        self.size = 0x1000  # 4 КБ памяти
        self.memory = bytearray(self.size)
    
    def read(self, address):
        if 0 <= address < self.size:
            return self.memory[address]
        raise ValueError(f"Адрес {hex(address)} вне диапазона памяти")
    
    def write(self, address, value):
        if 0 <= address < self.size:
            self.memory[address] = value & 0xFF
        else:
            raise ValueError(f"Адрес {hex(address)} вне диапазона памяти")
