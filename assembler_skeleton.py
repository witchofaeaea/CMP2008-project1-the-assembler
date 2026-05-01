# Student information
# Name: Hatice
# Surname: Yaşasın
# ID: 2104423

import sys
import csv
import glob
import os

def load_opcode_map():
    """Return a dictionary mapping instruction names to format and opcode.
       Create the opcode map dictionary with the instruction data.
    """
    # Hardcoded map based on the required subset from the project prompt.
    # Note: I-format opcodes are right-shifted by 1 (e.g., ADDI 1160 >> 1 = 580)
    opcode_map = {
        'ADD':  ('R', 1112),
        'SUB':  ('R', 1624),
        'ADDI': ('I', 580),
        'SUBI': ('I', 836),
        'LDUR': ('D', 1986),
        'STUR': ('D', 1984),
        'CBZ':  ('CB', 180),
        'B':    ('B', 5)
    }
    return opcode_map


def to_twos_complement(val, bits):
    """Convert signed integer to two's complement representation in 'bits' width."""
    if val < 0:
        val = (1 << bits) + val
    return val & ((1 << bits) - 1)


def tokenize(line):
    """
    Upgraded Tokenizer: Safely extracts registers and handles LEGv8 aliases.
    """
    # Remove comments
    line = line.split('//')[0].split(';')[0].strip()
    if not line:
        return []

    # Replace commas and brackets with spaces
    clean_line = line.replace(',', ' ').replace('[', ' ').replace(']', ' ')
    raw_tokens = clean_line.split()
    
    parsed_tokens = []
    for t in raw_tokens:
        t = t.upper()
        # Handle special LEGv8 register aliases
        if t == 'XZR':
            parsed_tokens.append('31')
        elif t == 'SP': 
            parsed_tokens.append('28') # In typical LEGv8 subsets, SP maps to 28
        elif t == 'FP':
            parsed_tokens.append('29')
        elif t == 'LR':
            parsed_tokens.append('30')
        # Safely strip 'X' from registers (like X12 -> 12)
        elif t.startswith('X') and t[1:].isdigit():
            parsed_tokens.append(t[1:])
        # Safely strip '#' from immediates (like #-16 -> -16)
        elif t.startswith('#'):
            parsed_tokens.append(t[1:])
        else:
            parsed_tokens.append(t)
            
    return parsed_tokens


def encode_instruction(line, opcode_map):
    machine_code = 0x11111111

    tokens = tokenize(line)
    if not tokens:
        return machine_code
        
    mnemonic = tokens[0]
    
    if mnemonic not in opcode_map:
        return machine_code
        
    fmt, opcode = opcode_map[mnemonic]
    
    try:
        # Using int(..., 0) allows Python to automatically handle base-10 OR base-16 (0x...) inputs
        
        if fmt == 'R':
            rd = int(tokens[1], 0)
            rn = int(tokens[2], 0)
            rm = int(tokens[3], 0)
            shamt = 0 
            
            # Edge Case: Support optional shift amounts (e.g., ADD X1, X2, X3, LSL #2)
            if len(tokens) >= 6 and tokens[4] == 'LSL':
                shamt = int(tokens[5], 0)
                
            machine_code = (opcode << 21) | (rm << 16) | (shamt << 10) | (rn << 5) | rd

        elif fmt == 'I':
            rd = int(tokens[1], 0)
            rn = int(tokens[2], 0)
            imm12 = int(tokens[3], 0)
            
            imm12_encoded = to_twos_complement(imm12, 12)
            machine_code = (opcode << 22) | (imm12_encoded << 10) | (rn << 5) | rd

        elif fmt == 'D':
            rt = int(tokens[1], 0)
            rn = int(tokens[2], 0)
            
            # Edge Case: Support omitted offset (e.g., LDUR X1, [X2] implies offset 0)
            offset = int(tokens[3], 0) if len(tokens) > 3 else 0
            op2 = 0 
            
            offset_encoded = to_twos_complement(offset, 9)
            machine_code = (opcode << 21) | (offset_encoded << 12) | (op2 << 10) | (rn << 5) | rt

        elif fmt == 'CB':
            rt = int(tokens[1], 0)
            offset = int(tokens[2], 0)
            
            offset_encoded = to_twos_complement(offset, 19)
            machine_code = (opcode << 24) | (offset_encoded << 5) | rt

        elif fmt == 'B':
            offset = int(tokens[1], 0)
            
            offset_encoded = to_twos_complement(offset, 26)
            machine_code = (opcode << 26) | offset_encoded

    except (IndexError, ValueError) as e:
        print(f"Error parsing line '{line}': {e}", file=sys.stderr)
        return 0x11111111

    return machine_code
        
    fmt, opcode = opcode_map[mnemonic]
    
    try:
        # ----------------------------------------
        # R-Format: ADD Rd, Rn, Rm
        # Layout: Opcode (11) | Rm (5) | shamt (6) | Rn (5) | Rd (5)
        # ----------------------------------------
        if fmt == 'R':
            rd = int(tokens[1])
            rn = int(tokens[2])
            rm = int(tokens[3])
            shamt = 0 # shamt is 0 for basic ADD/SUB
            
            machine_code = (opcode << 21) | (rm << 16) | (shamt << 10) | (rn << 5) | rd

        # ----------------------------------------
        # I-Format: ADDI Rd, Rn, #imm
        # Layout: Opcode (10) | imm12 (12) | Rn (5) | Rd (5)
        # ----------------------------------------
        elif fmt == 'I':
            rd = int(tokens[1])
            rn = int(tokens[2])
            imm12 = int(tokens[3])
            
            imm12_encoded = to_twos_complement(imm12, 12)
            machine_code = (opcode << 22) | (imm12_encoded << 10) | (rn << 5) | rd

        # ----------------------------------------
        # D-Format: LDUR Rt, [Rn, #offset]
        # Layout: Opcode (11) | address (9) | op2 (2) | Rn (5) | Rt (5)
        # ----------------------------------------
        elif fmt == 'D':
            rt = int(tokens[1])
            rn = int(tokens[2])
            offset = int(tokens[3])
            op2 = 0 # op2 is 0 for basic LDUR/STUR
            
            offset_encoded = to_twos_complement(offset, 9)
            machine_code = (opcode << 21) | (offset_encoded << 12) | (op2 << 10) | (rn << 5) | rt

        # ----------------------------------------
        # CB-Format: CBZ Rt, offset
        # Layout: Opcode (8) | address (19) | Rt (5)
        # ----------------------------------------
        elif fmt == 'CB':
            rt = int(tokens[1])
            offset = int(tokens[2])
            
            offset_encoded = to_twos_complement(offset, 19)
            machine_code = (opcode << 24) | (offset_encoded << 5) | rt

        # ----------------------------------------
        # B-Format: B offset
        # Layout: Opcode (6) | address (26)
        # ----------------------------------------
        elif fmt == 'B':
            offset = int(tokens[1])
            
            offset_encoded = to_twos_complement(offset, 26)
            machine_code = (opcode << 26) | offset_encoded

    except (IndexError, ValueError) as e:
        print(f"Error parsing line '{line}': {e}", file=sys.stderr)
        return 0x11111111

    return machine_code


def main():
    """Assemble every .s file under tests/ and write a corresponding .hex file.

    Students do not need to modify this function; it's provided so they can
    focus on the encoding logic.  Grading script will run this module and
    compare outputs in the outputs/ directory against expected results.
    """
    opcode_map = load_opcode_map()

    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    test_files = sorted(glob.glob("tests/*.s"))
    if not test_files:
        print("No test files found", file=sys.stderr)
        sys.exit(1)

    for input_file in test_files:
        base = os.path.splitext(os.path.basename(input_file))[0]
        out_path = f"outputs/{base}.hex"
        with open(input_file) as fin, open(out_path, 'w') as fout:
            for line in fin:
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                code = encode_instruction(line, opcode_map)
                if code is not None:
                    fout.write(f"0x{code:08X}\n")


if __name__ == "__main__":
    main()
    
