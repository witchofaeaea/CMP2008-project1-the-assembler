# Student information
# Name: Hatice
# Surname: Yaşasın
# ID: 2104423

import sys
import os
import glob
from pathlib import Path

def load_opcode_map():
    """Return a dictionary mapping instruction names to format and opcode."""
    return {
        "ADD":  {"format": "R",  "opcode": 0x458}, 
        "SUB":  {"format": "R",  "opcode": 0x658}, 
        "ADDI": {"format": "I",  "opcode": 0x488}, 
        "SUBI": {"format": "I",  "opcode": 0x688}, 
        "LDUR": {"format": "D",  "opcode": 0x7C2}, 
        "STUR": {"format": "D",  "opcode": 0x7C0}, 
        "CBZ":  {"format": "CB", "opcode": 0xB4},  
        "B":    {"format": "B",  "opcode": 0x05}   
    }

def to_twos_complement(val, bits):
    """Convert signed integer to two's complement representation."""
    if val < 0:
        val = (1 << bits) + val
    return val & ((1 << bits) - 1)

def get_reg(reg_str):
    """Clean and convert register string to integer."""
    # Remove X, brackets, commas, and spaces
    for char in "X[], ":
        reg_str = reg_str.replace(char, "")
    if reg_str.upper() == "ZR":
        return 31
    return int(reg_str)

def get_imm(imm_str):
    """Clean and extract numeric value from immediate string."""
    # Remove #, brackets, commas, and spaces
    for char in "#[], ":
        imm_str = imm_str.replace(char, "")
    return int(imm_str)

def encode_instruction(line, opcode_map):
    """Return 32-bit integer encoding for a single line of assembly."""
    # Tokenize by replacing delimiters with spaces then splitting
    parts = line.replace(',', ' ').replace('[', ' ').replace(']', ' ').split()
    if not parts:
        return None

    instr = parts[0].upper()
    if instr not in opcode_map:
        return 0x11111111

    info = opcode_map[instr]
    fmt = info["format"]
    op = info["opcode"]

    try:
        if fmt == "R":
            # [op:11][Rm:5][shamt:6][Rn:5][Rd:5]
            rd, rn, rm = get_reg(parts[1]), get_reg(parts[2]), get_reg(parts[3])
            return (op << 21) | (rm << 16) | (0 << 10) | (rn << 5) | rd

        elif fmt == "I":
            # [op:10][imm:12][Rn:5][Rd:5]
            rd, rn, imm = get_reg(parts[1]), get_reg(parts[2]), get_imm(parts[3])
            imm_bin = to_twos_complement(imm, 12)
            return (op << 22) | (imm_bin << 10) | (rn << 5) | rd

        elif fmt == "D":
            # [op:11][imm:9][op2:2][Rn:5][Rt:5]
            rt, rn, imm = get_reg(parts[1]), get_reg(parts[2]), get_imm(parts[3])
            imm_bin = to_twos_complement(imm, 9)
            return (op << 21) | (imm_bin << 12) | (0 << 10) | (rn << 5) | rt

        elif fmt == "CB":
            # [op:8][imm:19][Rt:5]
            rt, imm = get_reg(parts[1]), get_imm(parts[2])
            imm_bin = to_twos_complement(imm, 19)
            return (op << 24) | (imm_bin << 5) | rt

        elif fmt == "B":
            # [op:6][imm:26]
            imm = get_imm(parts[1])
            imm_bin = to_twos_complement(imm, 26)
            return (op << 26) | imm_bin

    except Exception:
        return 0x11111111
    
    return 0x11111111

def main():
    opcode_map = load_opcode_map()
    
    # Use absolute paths relative to this script's location
    root_dir = Path(__file__).resolve().parent
    tests_dir = root_dir / "tests"
    outputs_dir = root_dir / "outputs"

    if not outputs_dir.exists():
        outputs_dir.mkdir(parents=True, exist_ok=True)

    test_files = sorted(tests_dir.glob("*.s"))
    
    for input_file in test_files:
        out_path = outputs_dir / f"{input_file.stem}.hex"
        
        with input_file.open('r', encoding='utf-8') as fin, \
             out_path.open('w', encoding='utf-8') as fout:
            for line in fin:
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                
                code = encode_instruction(line, opcode_map)
                if code is not None:
                    fout.write(f"0x{code:08X}\n")

if __name__ == "__main__":
    main()
