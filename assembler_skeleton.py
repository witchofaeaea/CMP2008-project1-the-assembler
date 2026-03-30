# Student information
# Name: ________________________________
# Surname: _____________________________
# ID: _________________________________

import sys
import csv
import glob
import os



def load_opcode_map():
    """Return a dictionary mapping instruction names to format and opcode.
        Create the opcode map dictionary with the instruction data.

    """
    # TODO: build the opcode_map dictionary with all instructions from instruction_table.csv
    opcode_map = {

    }
    return opcode_map


def to_twos_complement(val, bits):
    """Convert signed integer to two's complement representation in 'bits' width."""

    return val


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
    # default wrong value so output files are created even with no logic
    machine_code = 0x11111111

    # TODO: implement instruction parsing and bitwise assembly
    # Start by tokenizing the line, then lookup format/opcode,
    # extract fields, and construct the machine_code

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