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
        "ADDI": {"format": "I",  "opcode": 0x244}, # Fixed 10-bit opcode
        "SUBI": {"format": "I",  "opcode": 0x344}, # Fixed 10-bit opcode
        "LDUR": {"format": "D",  "opcode": 0x7C2, "op2": 1}, # Added op2 field
        "STUR": {"format": "D",  "opcode": 0x7C0, "op2": 3}, # Added op2 field
        "CBZ":  {"format": "CB", "opcode": 0xB4},  
        "B":    {"format": "B",  "opcode": 0x05}   
    }

def to_twos_complement(val, bits):
    """Convert signed integer to two's complement representation."""
    if val < 0:
        val = (1 << bits) + val
    return val & ((1 << bits) - 1)

def clean_token(token):
    """Removes X, #, [, ], and commas to get a pure number."""
    t = token.upper()
    for char in "X#[],":
        t = t.replace(char, "")
    return t

def encode_instruction(line, opcode_map):
    """Return 32-bit integer encoding for a single line of assembly."""
    line = line.replace(',', ' ').replace('[', ' ').replace(']', ' ')
    parts = line.split()
    
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
            rd = int(clean_token(parts[1]))
            rn = int(clean_token(parts[2]))
            rm = int(clean_token(parts[3]))
            return (op << 21) | (rm << 16) | (0 << 10) | (rn << 5) | rd

        elif fmt == "I":
            rd = int(clean_token(parts[1]))
            rn = int(clean_token(parts[2]))
            imm = to_twos_complement(int(clean_token(parts[3])), 12)
            return (op << 22) | (imm << 10) | (rn << 5) | rd

        elif fmt == "D":
            rt = int(clean_token(parts[1]))
            rn = int(clean_token(parts[2]))
            imm = to_twos_complement(int(clean_token(parts[3])), 9)
            op2 = info.get("op2", 0) # Pull the specific op2 requirement 
            return (op << 21) | (imm << 12) | (op2 << 10) | (rn << 5) | rt

        elif fmt == "CB":
            rt = int(clean_token(parts[1]))
            imm = to_twos_complement(int(clean_token(parts[2])), 19)
            return (op << 24) | (imm << 5) | rt

        elif fmt == "B":
            imm = to_twos_complement(int(clean_token(parts[1])), 26)
            return (op << 26) | imm

    except Exception:
        return 0x11111111
        
    return 0x11111111

def main():
    opcode_map = load_opcode_map()
    root = Path(__file__).resolve().parent
    tests_dir = root / "tests"
    out_dir = root / "outputs"
    
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)

    test_files = sorted(tests_dir.glob("*.s"))
    
    for input_file in test_files:
        out_path = out_dir / f"{input_file.stem}.hex"
        
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
