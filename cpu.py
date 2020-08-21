import sys

class CPU:
    
    def __init__(self):

        self.ram = [0] * 256

        self.reg = [0] * 8

        self.pc = 0

        self.sp = 7

        self.reg[self.sp] = 0xF4

        self.ir = 0

        self.fl = 6

        self.table = {
            0b00000001: self.hlt,
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b10100010: self.mul,
            0b10100000: self.add,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret,
            0b10100111: self.cmpp,
            0b01010100: self.jmp,
            0b01010110: self.jeq,
            0b01010110: self.jne
        }

    def load(self):

        address = 0
    
        with open("sctest.ls8", "r") as f:
            for line in f:
                comment_split = line.split("#")
                n = comment_split[0].strip()

                if n == '':
                    continue

                try:
                    value = int(n, 2)
                except ValueError:
                    self.ram[address] = value
                    address += 1

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def prn(self, operand_a):
        print(self.reg[operand_a])

    def add(self, operand_a, operand_b):
        self.reg[operand_a] += self.reg[operand_b]

    def mul(self, operand_a, operand_b):
        self.reg[operand_a] = self.reg[operand_a] * self.reg[operand_b]

    def push(self, operand_a):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.reg[operand_a]

    def pop(self, operand_a):
        self.reg[operand_a] = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    def call(self, operand_a):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 2
        self.pc = self.reg[operand_a]
        return True

    def ret(self, operand_a):
        self.pop(operand_a)
        self.pc = self.reg[operand_a]
        return True

    def cmpp(self, operand_a, operand_b):
        a = self.reg[operand_a]
        b = self.reg[operand_b]

        if a == b:
            self.reg[self.fl] = 1
        elif a > b:
            self.reg[self.fl] = 2
        else:
            self.reg[self.fl] = 4
    
    def jmp(self, operand_a):
        self.pc = self.reg[operand_a]
        return True

    def jne(self, operand_a):
        v = self.reg[self.fl]
        if v == 2 or v == 4:
            return self.jmp(operand_a)

    def jeq(self, operand_a):
        if self.reg[self.fl] == 1:
            return self.jmp(operand_a)

    def hlt(self):
        sys.exit()

    def run(self):

        while True:
        
            self.ir = self.ram_read(self.pc)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            jump = self.table[self.ir](operand_a, operand_b)
            if not jump:
                self.pc += (self.ir >> 6) + 1