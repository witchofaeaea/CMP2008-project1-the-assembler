# Student information
# Name: Hatice
# Surname: Yaşasın
# ID: 2104423

import sys
import os
import glob

def load_opcode_map():
    """Return a dictionary mapping instruction names to format and opcode."""
    # Opcode mapping based on LEGv8 specifications
    opcode_map = {
        "ADD":  {"format": "R",  "opcode": 0x458}, # 1112 in decimal
        "SUB":  {"format": "R",  "opcode": 0x658}, # 1624 in decimal
        "ADDI": {"format": "I",  "opcode": 0x488}, # 1160-1161
        "SUBI": {"format": "I",  "opcode": 0x688}, # 1672-1673
        "LDUR": {"format": "D",  "opcode": 0x7C2}, # 1986
        "STUR": {"format": "D",  "opcode": 0x7C0}, # 1984
        "CBZ":  {"format": "CB", "opcode": 0xB4},  # 180
        "B":    {"format": "B",  "opcode": 0x05}   # 5
    }
    return opcode_map

def to_twos_complement(val, bits):
    """Convert signed integer to two's complement representation in 'bits' width."""
    if val < 0:
        val = (1 << bits) + val
    return val & ((1 << bits) - 1)

def get_reg(reg_str):
    """Helper to convert register string like 'X15' or 'XZR' to integer."""
    reg_str = reg_str.upper().replace('X', '').replace('[', '').replace(']', '').replace(',', '')
    if reg_str == 'ZR':
        return 31
    return int(reg_str)

def get_imm(imm_str):
    """Helper to extract numeric value from '#10' or '#-5'."""
    return int(imm_str.replace('#', '').replace(',', '').replace(']', ''))

def encode_instruction(line, opcode_map):
    """Return 32-bit integer encoding for *line*."""
    # Tokenize: remove commas and brackets, then split
    clean_line = line.replace(',', ' ').replace('[', ' ').replace(']', ' ')
    tokens = clean_line.split()
    
    if not tokens:
        return 0x11111111

    instr = tokens[0].upper()
    if instr not in opcode_map:
        raise ValueError(f"Unknown instruction: {instr}")

    info = opcode_map[instr]
    fmt = info["format"]
    op = info["opcode"]
    res = 0

    try:
        if fmt == "R":
            # ADD Rd, Rn, Rm -> [op:11][Rm:5][shamt:6][Rn:5][Rd:5]
            rd = get_reg(tokens[1])
            rn = get_reg(tokens[2])
            rm = get_reg(tokens[3])
            res = (op << 21) | (rm << 16) | (0 << 10) | (rn << 5) | rd

        elif fmt == "I":
            # ADDI Rd, Rn, #imm -> [op:10][imm:12][Rn:5][Rd:5]
            rd = get_reg(tokens[1])
            rn = get_reg(tokens[2])
            imm = to_twos_complement(get_imm(tokens[3]), 12)
            res = (op << 22) | (imm << 10) | (rn << 5) | rd

        elif fmt == "D":
            # LDUR Rt, [Rn, #imm] -> [op:11][imm:9][op2:2][Rn:5][Rt:5]
            rt = get_reg(tokens[1])
            rn = get_reg(tokens[2])
            imm = to_twos_complement(get_imm(tokens[3]), 9)
            res = (op << 21) | (imm << 12) | (0 << 10) | (rn << 5) | rt

        elif fmt == "CB":
            # CBZ Rt, #imm -> [op:8][imm:19][Rt:5]
            rt = get_reg(tokens[1])
            imm = to_twos_complement(get_imm(tokens[2]), 19)
            res = (op << 24) | (imm << 5) | rt

        elif fmt == "B":
            # B #imm -> [op:6][imm:26]
            imm = to_twos_complement(get_imm(tokens[1]), 26)
            res = (op << 26) | imm

    except Exception as e:
        print(f"Error parsing line '{line}': {e}")
        return 0x11111111

    return res

def main():
    opcode_map = load_opcode_map()

    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    test_files = sorted(glob.glob("tests/*.s"))
    if not test_files:
        print("No test files found", file=sys.stderr)
        return

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
    
