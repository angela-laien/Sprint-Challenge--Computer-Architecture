import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
ADD = 0b10100000
SUB = 0b10100001
DIV = 0b10100011
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    
    def __init__(self):

        self.table = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b10100000: self.ADD,
            0b10100001: self.SUB,
            0b10100011: self.DIV,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100111: self.CMP,
            0b01010100: self.JMP,
            0b01010101: self.JEQ,
            0b01010110: self.JNE
        }

        self.ram = [0] * 256

        self.reg = [0] * 8

        self.pc = 0

        self.sp = 7

        self.reg[self.sp] = 0xF4

        self.fl = 0b00000000
        
        self.running = False

    def load(self):

        address = 0
    
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    comment_split = line.split("#")
                    n = comment_split[0].strip()

                    if n == '':
                        continue

                    value = int(n, 2)

                    self.ram[address] = value
                    address += 1
        except:
            print("can not find it!")
            sys.exit()

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def LDI(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.reg[operand_a] = operand_b
        self.pc += 3

    def PRN(self):
        operand_a = self.ram[self.pc + 1]
        print(self.reg[operand_a])
        self.pc += 2

    def ADD(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.reg[operand_a] += self.reg[operand_b]
        self.pc += 3

    def MUL(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.reg[operand_a] = self.reg[operand_a] * self.reg[operand_b]
        self.pc += 3

    def SUB(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.reg[operand_a] -= self.reg[operand_b]
        self.pc += 3

    def DIV(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        if operand_b == 0:
            self.table[0b00000001]()
        else:
            self.reg[operand_a] = self.reg[operand_a] // self.reg[operand_b]
            self.pc += 3

    def PUSH(self):
        operand_a = self.ram[self.pc + 1]
        self.reg[self.sp] -= 1
        # register the value given to the address pointed by SP
        self.ram[self.reg[self.sp]] = self.reg[operand_a]
        self.pc += 2

    def POP(self):
        operand_a = self.ram[self.pc + 1]
        # copy value from the address pointed by SP to the register
        self.reg[operand_a] = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    def CALL(self):
        operand_a = self.ram[self.pc + 1]
        self.reg[self.sp] -= 1
        # compute return address and push to stack
        self.ram[self.reg[self.sp]] = self.pc + 2
        # set the pc value to the given register
        self.pc = self.reg[operand_a]

    def RET(self):
        # pop the return address from stack and set to pc
        self.pc = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    def CMP(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        a = self.reg[operand_a]
        b = self.reg[operand_b]
        #0b00000LGE
        if a == b:
            self.fl = 0b00000001
        elif a > b:
            self.fl = 0b00000010
        else:
            self.fl = 0b00000100
        self.pc += 3
    
    def JMP(self):
        # jump to address in the given register
        operand_a = self.ram[self.pc + 1]
        # set pc to that address
        self.pc = self.reg[operand_a]

    def JNE(self):
        operand_a = self.ram[self.pc + 1]
        # if equal flag is false
        if self.fl & 0b00000001 == 0:
            # jump to address in the given register
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def JEQ(self):
        operand_a = self.ram[self.pc + 1]
        if self.fl & 0b00000001 == 1:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def HLT(self):
        self.running = False
        self.pc += 1

    def run(self):

        self.running = True

        while self.running:
            ir = self.ram[self.pc]
            if ir in self.table:
                instruction = self.table[ir]
                instruction()
            else:
                self.running = False