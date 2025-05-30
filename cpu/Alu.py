class Alu:
    def __init__(self, cpu):
        self.cpu = cpu
    
    def _update_flags(self, result, carry=False):
        """Обновляет флаги процессора на основе результата операции"""
        # Обновляем флаг Zero (Z)
        self.cpu.flags[0x01].write(0x01 if result == 0x00 else 0x00)
        
        # Обновляем флаг Carry (C)
        self.cpu.flags[0x02].write(0x01 if carry else 0x00)
    
    def add(self, a, b):
        result = a + b
        carry = result > 0xFF
        result = result & 0xFF
        self._update_flags(result, carry)
        return result
    
    def sub(self, a, b):
        result = a - b
        carry = a < b  # Заем при вычитании
        result = result & 0xFF
        self._update_flags(result, carry)
        return result
    
    def xor(self, a, b):
        result = (a ^ b) & 0xFF
        self._update_flags(result, False)  # XOR не влияет на carry
        return result
    
    def or_op(self, a, b):
        result = (a | b) & 0xFF
        self._update_flags(result, False)  # OR не влияет на carry
        return result
    
    def and_op(self, a, b):
        result = (a & b) & 0xFF
        self._update_flags(result, False)  # AND не влияет на carry
        return result
    
    def not_op(self, a):
        result = (~a) & 0xFF
        self._update_flags(result, False)  # NOT не влияет на carry
        return result
    
    def shl(self, a):
        carry = (a & 0x80) != 0  # Проверяем старший бит
        result = (a << 1) & 0xFF
        self._update_flags(result, carry)
        return result
    
    def shr(self, a):
        carry = (a & 0x01) != 0  # Проверяем младший бит
        result = (a >> 1) & 0xFF
        self._update_flags(result, carry)
        return result
    
    def cmp(self, a, b):
        """Сравнение двух значений (как SUB, но без записи результата)"""
        result = a - b
        carry = a < b
        result = result & 0xFF
        self._update_flags(result, carry)
        # CMP не возвращает результат, только устанавливает флаги
