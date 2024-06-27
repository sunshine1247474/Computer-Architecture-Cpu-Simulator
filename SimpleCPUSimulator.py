from tabulate import tabulate

# Handles cache (stored information for quick access) operations (enabled, disabled, and flushed)
class Cache:
    def __init__(self):
        self.cache_enabled = False  # Cache is initially disabled
        self.cache = {}  # Cache storage

    def set_cache(self, address, value):
        if self.cache_enabled:  # Only set cache if enabled
            self.cache[address] = value  # Set cache value at address

    def get_cache(self, address):
        return self.cache.get(address, None)  # Get value from cache if available

    def enable_cache(self):
        self.cache_enabled = True  # Enable cache

    def disable_cache(self):
        self.cache_enabled = False  # Disable cache

    def flush_cache(self):
        self.cache = {}  # Clear the cache


# Represents the memory bus with read and write operations
class MemoryBus:
    def __init__(self):
        self.memory = [0] * 256  # Example memory size (256 addresses)

    def write(self, address, value):
        self.memory[address] = value  # Write value to memory at specified address

    def read(self, address):
        return self.memory[address]  # Read value from memory at specified address


# Simulates a CPU with registers, program counter, cache, and memory bus
class CPU:
    def __init__(self):
        self.registers = [0] * 8  # Example register count (8 registers)
        self.pc = 0  # Program counter
        self.cache = Cache()  # Initialize cache
        self.memory_bus = MemoryBus()  # Initialize memory bus
        self.instructions = {
            'ADD': self.add,
            'ADDI': self.addi,
            'SUB': self.sub,
            'SLT': self.slt,
            'BNE': self.bne,
            'J': self.jmp,
            'JAL': self.jal,
            'LW': self.lw,
            'SW': self.sw,
            'CACHE': self.cache_op,
            'HALT': self.halt
        }
        self.running = True  # CPU is initially running

    def add(self, rd, rs, rt):
        # R-type: Handles registers
        self.registers[rd] = self.registers[rs] + self.registers[rt]  # Perform addition
        print(f"ADD: R{rd} = R{rs} + R{rt} -> {self.registers[rd]}")

    def addi(self, rt, rs, immd):
        # I-type: Handles registers and immediate values
        self.registers[rt] = self.registers[rs] + immd  # Perform addition with immediate value
        print(f"ADDI: R{rt} = R{rs} + {immd} -> {self.registers[rt]}")

    def sub(self, rd, rs, rt):
        # R-type: Handles registers
        self.registers[rd] = self.registers[rs] - self.registers[rt]  # Perform subtraction
        print(f"SUB: R{rd} = R{rs} - R{rt} -> {self.registers[rd]}")

    def slt(self, rd, rs, rt):
        # R-type: Handles registers
        self.registers[rd] = 1 if self.registers[rs] < self.registers[rt] else 0  # Set less than
        print(f"SLT: R{rd} = 1 if R{rs} < R{rt} else 0 -> {self.registers[rd]}")

    def bne(self, rs, rt, offset):
        # Branch and Jump: Handles branches and jumps
        if self.registers[rs] != self.registers[rt]:  # Branch if not equal
            self.pc += offset  # Adjust program counter
        print(f"BNE: If R{rs} != R{rt}, PC = {self.pc}")

    def jmp(self, target):
        # Branch and Jump: Handles branches and jumps
        self.pc = target  # Jump to target address
        print(f"J: PC = {self.pc}")

    def jal(self, target):
        # Branch and Jump: Handles branches and jumps
        self.registers[7] = self.pc + 1  # Store return address in R7
        self.pc = target  # Jump to target address
        print(f"JAL: R7 = {self.pc + 1}, PC = {self.pc}")

    def lw(self, rt, offset, rs):
        # I-type: Handles registers and immediate values
        address = self.registers[rs] + offset  # Calculate memory address
        value = self.cache.get_cache(address)  # Check cache first
        if value is None:
            value = self.memory_bus.read(address)  # Read from memory if not in cache
            self.cache.set_cache(address, value)  # Update cache
        self.registers[rt] = value  # Load value into register
        print(f"LW: R{rt} = MEM[R{rs} + {offset}] -> {self.registers[rt]}")

    def sw(self, rt, offset, rs):
        # I-type: Handles registers and immediate values
        address = self.registers[rs] + offset  # Calculate memory address
        value = self.registers[rt]  # Get value from register
        self.memory_bus.write(address, value)  # Write value to memory
        self.cache.set_cache(address, value)  # Update cache
        print(f"SW: MEM[R{rs} + {offset}] = R{rt} -> {value}")

    def cache_op(self, code):
        # Cache Operations: Handles special operations
        if code == 0:
            self.cache.disable_cache()  # Disable cache
            print("CACHE: Disabled")
        elif code == 1:
            self.cache.enable_cache()  # Enable cache
            print("CACHE: Enabled")
        elif code == 2:
            self.cache.flush_cache()  # Flush cache
            print("CACHE: Flushed")

    def halt(self):
        # HALT: Handles special operations
        self.running = False  # Stop CPU execution
        print("HALT: Terminate execution")

    # Parses and executes an instruction
    def parse_instruction(self, instruction):
        parts = instruction.split(',')  # Split instruction into parts
        op = parts[0]  # Get operation code

        if op in ['ADD', 'SUB', 'SLT']:
            rd = int(parts[1][1:])  # Parse destination register
            rs = int(parts[2][1:])  # Parse source register 1
            rt = int(parts[3][1:])  # Parse source register 2
            self.instructions[op](rd, rs, rt)
        elif op == 'ADDI':
            rt = int(parts[1][1:])  # Parse target register
            rs = int(parts[2][1:])  # Parse source register
            immd = int(parts[3])  # Parse immediate value
            self.instructions[op](rt, rs, immd)
        elif op in ['BNE']:
            rs = int(parts[1][1:])  # Parse source register 1
            rt = int(parts[2][1:])  # Parse source register 2
            offset = int(parts[3])  # Parse offset
            self.instructions[op](rs, rt, offset)
        elif op in ['J', 'JAL']:
            target = int(parts[1])  # Parse target address
            self.instructions[op](target)
        elif op in ['LW', 'SW']:
            rt = int(parts[1][1:])  # Parse target register
            offset, rs = parts[2].split('(')  # Parse offset and source register
            offset = int(offset)  # Convert offset to integer
            rs = int(rs[:-1][1:])  # Convert source register to integer
            self.instructions[op](rt, offset, rs)
        elif op == 'CACHE':
            code = int(parts[1])  # Parse cache operation code
            self.instructions[op](code)
        elif op == 'HALT':
            self.instructions[op]()  # Execute HALT instruction
        else:
            raise ValueError(f"Unknown instruction: {op}")

    def run_program(self, program):
        self.pc = 0  # Reset program counter
        self.running = True  # Set CPU to running state
        while self.running and self.pc < len(program):
            self.parse_instruction(program[self.pc])  # Parse and execute current instruction
            self.pc += 1  # Move to the next instruction

    def display_registers(self):
        print("Registers:")
        register_table = [(i, val) for i, val in enumerate(self.registers)]  # Create register table
        print(tabulate(register_table, headers=["Register", "Value"], tablefmt="fancy_grid"))

    def display_memory(self):
        print("Memory:")
        memory_table = [(i, val) for i, val in enumerate(self.memory_bus.memory) if val != 0]  # Create memory table
        print(tabulate(memory_table, headers=["Address", "Value"], tablefmt="fancy_grid"))


# Reads instructions from a file
def fetch_instructions(instruction_input_file):
    with open(instruction_input_file, 'r') as file:
        instructions = file.readlines()  # Read instructions from file
    return [line.strip() for line in instructions]  # Strip newlines and return list


# Reads data from a file
def fetch_data(data_input_file):
    with open(data_input_file, 'r') as file:
        data = file.readlines()  # Read data from file
    return [line.strip() for line in data]  # Strip newlines and return list


# Initializes the memory bus with data from a file
def initialize_memory_bus(cpu, data_input_file):
    data_loaded = fetch_data(data_input_file)  # Load data from file
    for data in data_loaded:
        address, value = map(int, data.split(','))  # Parse address and value
        cpu.memory_bus.write(address, value)  # Write value to memory bus
        cpu.cache.set_cache(address, value)  # Optionally, set cache as well


# Sends instructions to the CPU for execution
def send_instructions_to_cpu(cpu, instruction_input_file):
    instructions_loaded = fetch_instructions(instruction_input_file)  # Load instructions from file
    cpu.run_program(instructions_loaded)  # Run loaded instructions on the CPU


def main():
    # File paths for instruction and data inputs
    INSTRUCTION_INPUT_FILE = "instruction_input.txt"
    DATA_INPUT_FILE = "data_input.txt"

    # Create a CPU instance
    cpu = CPU()

    # Print initialization messages
    print("---------------------------------------------------")
    print("Welcome to the Python CPU Simulator!")
    print("---------------------------------------------------")

    # Initialize Memory Bus with data from input file
    print("Initializing Memory Bus from data input file...")
    initialize_memory_bus(cpu, DATA_INPUT_FILE)
    print("Memory Bus successfully initialized")
    print("---------------------------------------------------")

    # Send instructions to the CPU for execution
    print("Sending instructions to CPU...")
    send_instructions_to_cpu(cpu, INSTRUCTION_INPUT_FILE)
    print("---------------------------------------------------")

    # Display final state of registers and memory
    print("Final State of Registers and Memory:")
    cpu.display_registers()
    cpu.display_memory()

    # Print termination message
    print("Terminating CPU Processing...")


# Entry point for the program
if __name__ == "__main__":
    main()
