"""
programs.py

Some test programs we can import into the REPL
"""

import machine
from opcodes import *

# Note how with the opcode names these programs look
# almost like assembler code, even though they are
# still valid Python data
PUSH_AND_HALT = [
    PUSH, 0x66, # PUSH 66
    HALT]       # HALT


ADD_TWO_AND_THREE = [
    PUSH, 0x2, # PUSH 2
    PUSH, 0x3, # PUSH 3
    ADD,       # ADD
    HALT]      # HALT

SUB_FIVE_FROM_TWO = [
    PUSH, 0x2, # PUSH 2
    PUSH, 0x5, # PUSH 5
    SUB,       # SUB
    HALT
]

JMP_IF_ZERO = [
    PUSH, 0x0,
    PUSH, 0x8,
    JZ,

    PUSH, 0x100, # This should never run
    HALT,

    # This should always run
    PUSH, 0x200,
    HALT
]

DONT_JMP_IF_NON_ZERO = [
    PUSH, 0x1,
    PUSH, 0x8,
    JZ,

    # This should always run
    PUSH, 0x100,
    HALT,

    # This should never run
    PUSH, 0x200,
    HALT
]

def test_machine():
    assert machine.run_code_for_result(ADD_TWO_AND_THREE) == 5
    assert machine.run_code_for_result(SUB_FIVE_FROM_TWO)
    assert machine.run_code_for_result(JMP_IF_ZERO) == 0x200
    assert machine.run_code_for_result(DONT_JMP_IF_NON_ZERO) == 0x100
