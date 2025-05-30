class Reg8:
    def __init__(self):
        self._value = 0x00
    
    def read(self):
        return self._value & 0xFF
    
    def write(self, value):
        self._value = value & 0xFF
        
    def __repr__(self):
        return f"{self._value:02X}"
