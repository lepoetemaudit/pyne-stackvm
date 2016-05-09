"""
opcodes.py

Define constants for our opcodes
"""

# Stack operations
PUSH = 0x01
POP = 0x02
COPY = 0x03
SWAP = 0x04

# Arithmetic operations
ADD = 0x20
SUB = 0x21

# Control operations
JZ = 0x30
JG = 0x31
JL = 0x32

# IO
PUTCH = 0x50
PUTDEC = 0x51
PUTHEX = 0x52
PUTS = 0x53

# Machine operations
HALT = 0x00
