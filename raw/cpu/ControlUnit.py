class ControlUnit:
    def __init__(self, cpu):
        self.cpu = cpu
        self.opcodes = {
            0x00: ("nop", 1),
            0x01: ("mov_r", 3),
            0x02: ("ld_r", 3),
            0x03: ("add_r", 2),
            0x04: ("sub_r", 2),
            0x05: ("xor_r", 2),
            0x06: ("or_r", 2),
            0x07: ("and_r", 2),
            0x08: ("not_r", 2),
            0x09: ("cmp_r", 3),
            0x0A: ("jmp_addr", 2),
            0x0B: ("je_addr", 2),
            0x0C: ("jne_addr", 2),
            0x0D: ("shl_r", 1),
            0x0E: ("shr_r", 1),
            0x0F: ("call_addr", 2),
            0x10: ("ret", 1),
            0x11: ("in_r", 1),
            0x12: ("out_r", 1),
            0x13: ("ldm_r", 3),
            0x14: ("ldm_r_pair", 3),
            0x15: ("push_r", 2),
            0x16: ("pop_r", 2),
            0x17: ("inc_r", 2),
            0x18: ("dec_r", 2),
            0x19: ("stm_addr", 3),
            0x1A: ("stm_pair", 3),
            0xff: ("hlt", 1)
        }
    
    def decode(self):
        opcode = (self.cpu.registers[0x06].read()) & 0xFF
        if opcode in self.opcodes:
            return self.opcodes[opcode]
        return None, 0

    def execute(self, opcode_name):
        
        #print(f"{opcode_name} : {hex(self.cpu.registers[0x05].read()-1)} | {self.cpu.registers}")
        
        if opcode_name == "nop":
            pass
        
        elif opcode_name == "mov_r":
            self.cpu.fetch()
            dest = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            src = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            bias = self.cpu.registers[0x06].read()
            
            value = self.cpu.registers[src].read() + bias
            self.cpu.registers[dest].write(value)
            
        elif opcode_name == "ld_r":
            self.cpu.fetch()
            src = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            value = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            bias = self.cpu.registers[0x06].read()
            
            self.cpu.registers[src].write(value)
            
        elif opcode_name == "add_r":
            self.cpu.fetch()
            a = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            b = self.cpu.registers[0x06].read()
            
            value = self.cpu.alu.add(self.cpu.registers[a].read(), self.cpu.registers[b].read())
            self.cpu.registers[a].write(value)
            
        elif opcode_name == "sub_r":
            self.cpu.fetch()
            a = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            b = self.cpu.registers[0x06].read()
            
            value = self.cpu.alu.sub(self.cpu.registers[a].read(), self.cpu.registers[b].read())
            self.cpu.registers[a].write(value)
            
        elif opcode_name == "xor_r":
            self.cpu.fetch()
            a = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            b = self.cpu.registers[0x06].read()
            
            value = self.cpu.alu.xor(self.cpu.registers[a].read(), self.cpu.registers[b].read())
            self.cpu.registers[a].write(value)
            
        elif opcode_name == "or_r":
            self.cpu.fetch()
            a = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            b = self.cpu.registers[0x06].read()
            
            value = self.cpu.alu.or_op(self.cpu.registers[a].read(), self.cpu.registers[b].read())
            self.cpu.registers[a].write(value)
            
        elif opcode_name == "and_r":
            self.cpu.fetch()
            a = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            b = self.cpu.registers[0x06].read()
            
            value = self.cpu.alu.and_op(self.cpu.registers[a].read(), self.cpu.registers[b].read())
            self.cpu.registers[a].write(value)
            
        elif opcode_name == "not_r":
            self.cpu.fetch()
            a = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            b = self.cpu.registers[0x06].read()
            
            value = self.cpu.alu.not_op(self.cpu.registers[a].read(), self.cpu.registers[b].read())
            self.cpu.registers[a].write(value)
            
        elif opcode_name == "shl_r":
            self.cpu.fetch()
            src = self.cpu.registers[0x06].read()
            value = self.cpu.registers[src].read()
            value = self.cpu.alu.shl(value)
            self.cpu.registers[src].write(value)
            
        elif opcode_name == "shr_r":
            self.cpu.fetch()
            src = self.cpu.registers[0x06].read()
            value = self.cpu.registers[src].read()
            value = self.cpu.alu.shr(value)
            self.cpu.registers[src].write(value)
            
        elif opcode_name == "cmp_r":
            self.cpu.fetch()
            a = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            b = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            mode = self.cpu.registers[0x06].read()
            
            # Получаем значения в зависимости от режима
            if mode == 0x00:  # R-R (регистр-регистр)
                val_a = self.cpu.registers[a].read()
                val_b = self.cpu.registers[b].read()
            elif mode == 0x01:  # R-V (регистр-значение)
                val_a = self.cpu.registers[a].read()
                val_b = b  # b уже содержит непосредственное значение
            elif mode == 0x02:  # V-R (значение-регистр)
                val_a = a  # a уже содержит непосредственное значение
                val_b = self.cpu.registers[b].read()
            elif mode == 0x03:  # V-V (значение-значение)
                val_a = a  # a уже содержит непосредственное значение
                val_b = b  # b уже содержит непосредственное значение
            else:
                raise ValueError(f"Неизвестный режим CMP: {mode}")
            
            # Выполняем сравнение
            self.cpu.alu.cmp(val_a, val_b)
            
        elif opcode_name == "jmp_addr":
            self.cpu.fetch()
            high = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            low = self.cpu.registers[0x06].read()
            
            addr = (high << 8) | low
            self.cpu.registers[0x05].write(addr)
            
        elif opcode_name == "je_addr":
            self.cpu.fetch()
            high = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            low = self.cpu.registers[0x06].read()
            
            if self.cpu.flags[0x01].read() == 0x01: # not 0
                addr = (high << 8) | low
                self.cpu.registers[0x05].write(addr)
                
        elif opcode_name == "jne_addr":
            self.cpu.fetch()
            high = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            low = self.cpu.registers[0x06].read()
            
            if self.cpu.flags[0x01].read() == 0x00: # is 0
                addr = (high << 8) | low
                self.cpu.registers[0x05].write(addr)
                
        elif opcode_name == "call_addr":
            self.cpu.fetch()
            high = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            low = self.cpu.registers[0x06].read()
            self.cpu.push(self.cpu.registers[0x05].read_l())
            self.cpu.push(self.cpu.registers[0x05].read_h())
            addr = (high << 8) | low
            self.cpu.registers[0x05].write(addr)
            # Для меня завтрашнего: Доделать call и ret, попросить сделать ассемблер, начать делать девайсы. Для call юзай код тз jmp, только адресы записывай в порядке - push(ip->low); push(ip->high).
            # Pop так-же, но в обратном порядке. Крч думаю ты понял, хд (пздц, пишу себе-же)
            # -- STACK --
            # ..
            # high
            # low
            # ..
            # -----------
            
        elif opcode_name == "ret":
            high = self.cpu.pop()
            low = self.cpu.pop()
            addr = (high << 8) | low
            self.cpu.registers[0x05].write(addr)
            
        elif opcode_name == "ldm_r":
            self.cpu.fetch()
            reg = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            high = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            low = self.cpu.registers[0x06].read()
            
            addr = (high << 8) | low
            
            value = self.cpu.ram.read(addr)
            self.cpu.registers[reg].write(value)
            
        elif opcode_name == "ldm_r_pair":
            self.cpu.fetch()
            reg = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            high_reg = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            low_reg = self.cpu.registers[0x06].read()
            
            high = self.cpu.registers[high_reg].read()
            low = self.cpu.registers[low_reg].read()
            
            addr = (high << 8) | low
            
            value = self.cpu.ram.read(addr)
            self.cpu.registers[reg].write(value)
            
        elif opcode_name == "in_r":
            self.cpu.fetch()
            port_reg = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            save_reg = self.cpu.registers[0x06].read()
            
            port = self.cpu.registers[port_reg].read()
            if hasattr(self.cpu, 'device_manager') and self.cpu.device_manager:
                value = self.cpu.device_manager.device_out(port)
                self.cpu.registers[save_reg].write(value)
            else:
                print(f"Нет менеджера устройств для порта {port}")

        elif opcode_name == "out_r":
            self.cpu.fetch()
            port_reg = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            value_reg = self.cpu.registers[0x06].read()
            
            port = self.cpu.registers[port_reg].read()
            value = self.cpu.registers[value_reg].read()
            
            if hasattr(self.cpu, 'device_manager') and self.cpu.device_manager:
                self.cpu.device_manager.device_in(port, value)
            else:
                print(f"Нет менеджера устройств для порта {port}")
                
        elif opcode_name == "push_r":
            self.cpu.fetch()
            reg = self.cpu.registers[0x06].read()
            value = self.cpu.registers[reg].read()
            self.cpu.push(value)
            
        elif opcode_name == "pop_r":
            self.cpu.fetch()
            reg = self.cpu.registers[0x06].read()
            value = self.cpu.pop()
            
            self.cpu.registers[reg].write(value)
            
        elif opcode_name == "inc_r":
            self.cpu.fetch()
            reg = self.cpu.registers[0x06].read()
            value = self.cpu.registers[reg].read()
            value = self.cpu.alu.add(value, 1)
            self.cpu.registers[reg].write(value)
            
        elif opcode_name == "dec_r":
            self.cpu.fetch()
            reg = self.cpu.registers[0x06].read()
            value = self.cpu.registers[reg].read()
            value = self.cpu.alu.sub(value, 1)
            self.cpu.registers[reg].write(value)
        
        elif opcode_name == "stm_addr":
            self.cpu.fetch()
            high = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            low = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            reg = self.cpu.registers[0x06].read()
            
            addr = (high << 8) | low
            
            self.cpu.ram.write(addr, self.cpu.registers[reg].read())
            
        elif opcode_name == "stm_pair":
            self.cpu.fetch()
            high_reg = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            low_reg = self.cpu.registers[0x06].read()
            self.cpu.fetch()
            reg = self.cpu.registers[0x06].read()
            
            print(high_reg, low_reg, reg)
            
            high = self.cpu.registers[high_reg].read()
            low = self.cpu.registers[low_reg].read()
            
            addr = (high << 8) | low
            
            self.cpu.ram.write(addr, self.cpu.registers[reg].read())
            
        elif opcode_name == "hlt":
            self.cpu.running = False
            