"""CPU functionality."""

import sys

# List of instructions codes


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # hold 256 bytes of memory
        self.ram = [0] * 256
        # hold 8 general-purpose registers
        self.reg = [0] * 8
        # program counter
        self.pc = 0
        # stack pointer
        self.sp = 7
        # CPU running
        self.running = True

        self.flags = {
            'E': 0,
            'G': 0,
            'L': 0,
        }

        self.ir = {
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b00000001: self.hlt,
            0b10100010: self.mul,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret,
            0b10100000: self.add,
            0b10100111: self.comp,
            0b01010101: self.jeq,
            0b01010110: self.jne,
            0b01010100: self.jmp
        }

    def hlt(self, op1, op2):
        self.running = False
        return (0, False)

    def ldi(self, op1, op2):
        self.reg[op1] = op2
        return(3, True)

    def prn(self, op1, op2):
        print(self.reg[op1])
        return(2, True)

    def mul(self, op1, op2):
        self.alu("MUL", op1, op2)
        return(3, True)

    def pop(self, op1, op2):
        self.reg[op1] = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        return(2, True)

    def push(self, op1, op2):
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[op1], self.reg[self.sp])
        return(2, True)

    def call(self, op1, op2):
        self.sp -= 1
        self.ram[self.sp] = self.pc + 2
        self.pc = self.reg[op1]
        return (0, True)

    def ret(self, op1, op2):
        self.pc = self.ram[self.sp]
        return (0, True)

    def add(self, op1, op2):
        self.alu('ADD', op1, op2)
        return (3, True)

    def comp(self, op1, op2):
        self.alu('CMP', op1, op2)
        return (3, True)

    def ram_read(self, address):
        if address < len(self.ram):
            return self.ram[address]
        else:
            print("address is too high:" + str(address))
            sys.exit(1)

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        address = 0
        if len(sys.argv) > 1:
            filename = sys.argv[1]
            try:
                with open(filename) as f:
                    for line in f:
                        num = line.split("#")[0].strip()

                        if num == '':
                            continue

                        val = int(num, 2)
                        self.ram[address] = val
                        address += 1

            except FileNotFoundError:
                print("File not find!")
                sys.exit(2)
            f.close()
        else:

            # For now, we've just hardcoded a program:

            program = [
                # From print8.ls8
                0b10000010,  # LDI R0,8
                0b00000000,
                0b00001000,
                0b01000111,  # PRN R0
                0b00000000,
                0b00000001,  # HLT
            ]

            for instruction in program:
                self.ram[address] = instruction
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'SUB':
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'CMP':
            if self.reg[reg_a] < self.reg[reg_b]:
                # less than L flag to 1
                self.flags['L'] = 1
                # greater than flag to 0
                self.flags['G'] = 0
                # equal to flag to 0
                self.flags['E'] = 0

            elif self.reg[reg_a] > self.reg[reg_b]:
                # greater than flag to 1
                self.flags['G'] = 1
                # less than flag to 0
                self.flags['L'] = 0
                # equal to flag to 0
                self.flags['E'] = 0
            else:
                # equal to flag to 1
                self.flags['E'] = 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            instruction_register = self.ram_read(self.pc)
            op1, op2 = self.ram_read(self.pc + 1), self.ram_read(self.pc + 2)
            # self.trace()
            try:
                out = self.ir[instruction_register](op1, op2)
                self.pc += out[0]

            except:
                print(f"Instruction not valid: {instruction_register}")
                sys.exit()
