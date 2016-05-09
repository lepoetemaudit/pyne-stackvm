"""
opcodes.py

Define constants for our opcodes
"""

# Stack operations
PUSH = 0x01
POP = 0x02

# Arithmetic operations
ADD = 0x20
SUB = 0x21

# Control operations
JZ = 0x30

# IO
PUTCH = 0x50
PUTDEC = 0x51
PUTHEX = 0x52

# Machine operations
HALT = 0x00
