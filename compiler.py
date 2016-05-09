"""
compiler.py

Compile strings into sequences of words, i.e. the native
code format of our virtual machine
"""

import string
import sys
import array


import opcodes
import machine

opcode_map = {
    "+": opcodes.ADD,
    "-": opcodes.SUB,
    "=": opcodes.SUB,  # Compare actually just subtracts
    "JZ": opcodes.JZ,
    "HALT": opcodes.HALT,
}

# Token types
STRING = "S"
NUMBER = "N"
INSTRUCTION = "I"
LABEL = "L"
LABEL_REF = "R"

class CompilerError(Exception):
    pass

def get_tokens(code):
    current_token = ""
    token_type = None
    line_number = 1
    while len(code):
        head = code[0]
        code = code[1:]

        # Token start
        if token_type is None:
            # Ignore whitespace by itself
            if head in string.whitespace:
                continue
            elif head in string.digits:
                token_type = NUMBER
                current_token += head
            elif head in string.ascii_letters + "-+/*=":
                token_type = INSTRUCTION
                current_token += head
            elif head == '"':
                token_type = STRING
            elif head == ":":
                token_type = LABEL
            elif head == "@":
                token_type = LABEL_REF

        elif token_type == NUMBER:
            if current_token=='0' and head=='x':
                # It's a hex number
                current_token += head
                continue
            
            if head in string.hexdigits:
                current_token += head
            elif head in string.digits:
                current_token += head
            elif head in string.whitespace:
                if current_token.startswith('0x'):
                    yield int(current_token, 16), NUMBER
                else:
                    yield int(current_token), NUMBER

                current_token = ''
                token_type = None
            else:
                raise CompilerError("Line %d: Bad character '%s' on number" % (
                    line_number, head))
        elif token_type == INSTRUCTION:
            if head in string.ascii_letters + "-+/*":
                current_token += head
            elif head in string.whitespace:
                opcode = opcode_map.get(current_token.upper())
                if opcode is None:
                    raise CompilerError("Line %d: Unknown opcode: %s" % (
                        line_number, current_token))

                yield opcode, INSTRUCTION
                current_token = ''
                token_type = None
            else:
                raise CompilerError("Line %d: Bad character '%s' on instruction" % (
                    line_number, head))
        elif token_type == STRING:
            if head == '"':
                yield current_token, STRING
                token_type = None
                current_token = ''
            else:
                current_token += head

        elif token_type in (LABEL, LABEL_REF):
            if head in string.ascii_letters:
                current_token += head
            elif head in string.whitespace:
                yield current_token, token_type
                token_type = None
                current_token = ''
            else:
                raise CompilerError("Line %d: Bad character '%s' on label" % (
                    line_number, head))
        if head == '\n':
            line_number += 1

    yield (current_token, token_type)

def compile_string(code): # type: (str) -> List[int]
    code_points = [] # type: List[int]
    symbol_table = []
    for token, typ in get_tokens(code + "\n"):
        if typ == NUMBER:
            code_points += [opcodes.PUSH, machine.w(token)]
        elif typ == STRING:
            # We reverse it so we it pops out in the right order
            for c in reversed(token):
                code_points += [opcodes.PUSH, ord(c)]
        elif typ == INSTRUCTION:
            code_points.append(token)

        elif typ == LABEL:
            print(typ, token)
            print(len(code_points))
            symbol_table.append((len(code_points), token))

        elif typ == LABEL_REF:
            code_points += [opcodes.PUSH, token]

    code_points.append(opcodes.HALT)

    # Do a final pass and replace any refs with their code positions
    output = []
    for c in code_points:
        if isinstance(c, str):
            try:
                label = next(l for l in symbol_table if c == l[1])
                output.append(label[0])
            except StopIteration:
                raise CompilerError("Unknown symbol: %s" % token)
        else:
            output.append(c)

    return output

def serialize(code):
    return array.array('h', code)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python compiler.py [source] [output]")
        sys.exit(-1)

    code = compile_string(open(sys.argv[1]).read())
    with open(sys.argv[2], 'w') as f:
        serialize(code).tofile(f)

