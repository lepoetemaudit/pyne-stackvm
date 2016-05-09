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

def test_machine():
    assert machine.run_code_for_result(ADD_TWO_AND_THREE) == 5
    assert machine.run_code_for_result(SUB_FIVE_FROM_TWO)
