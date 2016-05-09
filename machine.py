# Machine.py
# Define the inner workings of our stack-machine

from collections import namedtuple, deque
from typing import Optional, Tuple, Callable
import sys
import array
import os

import opcodes

MAIN_STACK_SIZE = 0x800
CALL_STACK_SIZE = 0x400

MAX_INT = 0x799F
MIN_INT = -0x8000

# Tuple definition for the state of our virtual machine
Machine = namedtuple(
    'Machine', 
    ['main_stack', 
     'call_stack', 
     'instruction_pointer', 
     'code']) # type: Tuple[deque, deque, int, list]

# Tuple definition describing an instruction
Instruction = namedtuple(
    'Instruction',
    ['opcode',
     'name',
     'execute']) # type: Tuple[int, int, str, str, Callable[[Machine], Machine]]


def describe_instruction(instruction): # type: (Instruction) -> str
    """
    Return a string representation of an Instruction
    """

    return "0x%.2x -> %s" % instruction[0:2]


class MachineError(BaseException):
    """
    Any runtime errors encountered when our machine is running
    """

    def __init__(self, message, machine): # (MachineError) -> MachineError
        super(MachineError, self).__init__(self, message)
        self.machine = machine


def w(val): # type: (int) -> int
    """
    Enforce the constraint of our 'machine' word (a 16bit signed int)
    """
    while val > MAX_INT:
        val -= 0x10000

    while val < MIN_INT:
        val += 0x10000 

    return val


def push_stack(machine, val): # type: (Machine, int) -> Machine
    """
    Helper for pushing to the main stack of a machine
    """

    if len(machine.main_stack) >= MAIN_STACK_SIZE:
        raise MachineError("Stack overflow: %x", machine)
    machine.main_stack.append(w(val))

    return machine
    

def pop_stack(machine): # type: (Machine) -> int
    if len(machine.main_stack) == 0:
        raise MachineError("Stack underflow: %x", machine)

    return machine.main_stack.pop()


def next_instruction(machine): # type: (Machine) -> Tuple[int, Machine]
    # Get the next instruction, return the updated machine state

    main_stack, call_stack, ip, code = machine

    # Bounds check on ip
    if ip >= len(code) or ip < 0:
        raise MachineError(
            "ip out of code range: ip=%d, code size=%d" % (ip, len(code)),
            machine)

    # Fetch next instruction opcode (or argument for certain opcodes)
    opcode = code[ip]

    # Increment instruction pointer
    ip += 1

    return opcode, Machine(main_stack, call_stack, ip, code)

    
# Define the implementation of our instructions

# 0x01 - PUSH
def _op_push(machine): # type: (Machine) -> Machine
    # Get the next code word as the value to push
    word, machine = next_instruction(machine) 
    return push_stack(machine, word)

# 0x20 - ADD
def _op_add(machine):
    return push_stack(
        machine, 
        pop_stack(machine) + pop_stack(machine))

# 0x21 - SUB
def _op_sub(machine):
    op2, op1 = (pop_stack(machine) for _ in range(2))
    return push_stack(machine, op1 - op2)

# 0x40 - JZ (Jump if zero)
def _op_jmp_zero(machine):
    new_ip, result = (pop_stack(machine) for _ in range(2))
    if result == 0:
        return Machine(
            machine.main_stack, machine.call_stack, new_ip, machine.code)
    return machine
    
dispatch_table = {
    # Stack operations
    opcodes.PUSH: Instruction(opcodes.PUSH, "PUSH", _op_push),
    
    # Arithmetic operations
    opcodes.ADD: Instruction(opcodes.ADD, "ADD", _op_add),
    opcodes.SUB: Instruction(opcodes.SUB, "SUB", _op_sub),

    # Control operations
    opcodes.JZ: Instruction(opcodes.JZ, "JZ", _op_jmp_zero)
}  # type: Dict[int, Instruction]


def make_machine(code=None): # type: (Optional[List[int]]) -> Machine
    """
    Instantiate a virtual stack-machine
    """
    return Machine(
        main_stack=deque(), 
        call_stack=deque(),
        instruction_pointer=0,
        code=code or [])



def step_machine(machine, debug=True):  # type: (Machine, Optional[bool]) -> Machine
    """
    Step the machine (i.e. execute the instruction at the current
    instruction_pointer.

    Returns the machine in the new current state.
    """
    opcode, machine = next_instruction(machine)

    # Match and execute on instruction with our dispatch table
    instruction = dispatch_table.get(opcode)
    if not instruction:
        raise MachineError("Got bad opcode: %x" % opcode, machine)
    if debug:
        print("++ Exec ip=%d [%s]" % (
            machine.instruction_pointer, 
            describe_instruction(instruction)))

    return instruction.execute(machine)


def run_machine(machine, debug=True):  # type: (Machine, Optional[bool]) -> Machine
    """
    Run the machine until it errors or we hit a HALT instruction
    """

    while True:
        # Bounds check
        if len(machine.code) <= machine.instruction_pointer:
             raise MachineError(
                "ip out of code range: ip=%d, code size=%d" % (
                    machine.instruction_pointer, 
                    len(machine.code)),
                machine)

        if machine.code[machine.instruction_pointer] == opcodes.HALT:
            if debug:
                print("++ HALT")
            return machine
        else:
            machine = step_machine(machine, debug)

def run_code_for_result(code, debug=False):
    """
    A shortcut for running some code and returning just the result
    """
    return run_machine(make_machine(code), debug).main_stack.pop()
    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python machine.py [program]")
        sys.exit(-1)
    else:
        size = os.path.getsize(sys.argv[1])
        code = array.array('h') # type: array.array
        code.fromfile(open(sys.argv[1]), size/2)
        print(run_code_for_result(code, debug=True))
    
