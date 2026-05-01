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
    Helper function to clean and split an assembly line into distinct tokens.
    Removes comments, commas, brackets, 'X' (registers), and '#' (immediates).
    """
    line = line.split('//')[0].split(';')[0].strip()
    
    if not line:
        return []

    clean_line = line.upper()
    clean_line = clean_line.replace(',', ' ').replace('[', ' ').replace(']', ' ')
    clean_line = clean_line.replace('X', '').replace('#', '')
    
    return clean_line.split()


def encode_instruction(line, opcode_map):
    """Return 32-bit integer encoding for *line*.

    STUDENT RESPONSIBILITIES:
      * tokenize the assembly text (remove commas, split whitespace)
      * lookup format/opcode in opcode_map (built from CSV)
      * for each format (R, I, D, CB, B) parse tokens to extract registers and immediates
      * convert immediates to two's complement when negative
      * assemble the final 32-bit integer with shifts and bitwise OR
      * return a default constant if not yet implemented so output file
        still exists (e.g. 0x11111111)
      * raise errors on unknown instructions

    Reference the LEGv8 quick reference guide for exact bit layouts of each format.
    """
    machine_code = 0x11111111

    tokens = tokenize(line)
    if not tokens:
        return machine_code # Empty line, though main() usually skips these
        
    mnemonic = tokens[0]
    
    if mnemonic not in opcode_map:
        print(f"Error: Unknown instruction '{mnemonic}'", file=sys.stderr)
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
    
