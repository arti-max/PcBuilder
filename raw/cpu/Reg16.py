class Reg16:
    def __init__(self):
        self._value = 0x00
    
    def read(self):
        return self._value & 0xFFFF
    
    def write(self, value):
        self._value = value & 0xFFFF
        
    def read_h(self):
        return (self._value >> 8) & 0xFF
    
    def read_l(self):
        return self._value & 0xFF

    def __repr__(self):
        return f"{self._value:04X}"