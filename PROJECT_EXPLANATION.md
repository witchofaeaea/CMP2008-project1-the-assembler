# CMP2008 Project 1: LEGv8 Assembler

## Overview
This project asks you to implement a subset of a LEGv8 assembler in `assembler_skeleton.py`.

You are to submit your entire project folder.

You must support the following instruction formats:
- R-format: `ADD`, `SUB`
- I-format: `ADDI`, `SUBI`
- D-format: `LDUR`, `STUR`
- CB-format: `CBZ`
- B-format: `B`

## Student responsibilities
1. Fill in your information at the top of `assembler_skeleton.py`:
   - `Name`
   - `Surname`
   - `ID`
2. Build the opcode map and implement `encode_instruction()` in `assembler_skeleton.py`.
3. Tokenize assembly lines, handle each supported format, and encode each instruction to a 32-bit integer.
4. Convert negative immediates to two's complement yourself.
   - I-format immediates use 12 bits.
   - D-format immediates use 9 bits.
   - CB-format branch offsets use 19 bits.
   - B-format branch offsets use 26 bits.
5. Do not use labels for branch targets in the tests; branch operands are numeric addresses written directly with `#`.

## Test files
The assembler is graded against the files in `answers/`.

Current tests include:
- `tests/test_r_format.s`
- `tests/test_b_format.s`
- `tests/test_i_format.s`
- `tests/test_d_format.s`
- `tests/test_cb_format.s`
- `tests/test_all.s` (all instruction types in one file)

The `test_all.s` file contains examples of every supported instruction type.

> Note: The provided tests use immediate values in positive form. You should still encode signed fields correctly using two's complement when required by the instruction format.

## Grading
This project is graded out of **100 points**.

The rubric is based on functional test coverage with higher weight for D-format and CB-format support:
- `test_r_format`: 12 points
- `test_b_format`: 12 points
- `test_i_format`: 10 points
- `test_all`: 15 points
- `test_d_format`: 25 points
- `test_cb_format`: 26 points

The grader compares generated `outputs/*.hex` files against `answers/*.hex`.

### What is required for a pass
- The assembler must generate the exact expected hex values.
- Missing output files or encoding errors will count as failure for that test.

## Running the auto-grader
The official grading script is not included in this starter template. Your submission will be graded by the course autograder on GitHub Classroom.

If a grader script is provided separately by the instructor, it can be run from the appropriate repository root.

The grader prints:
- student info read from the target file
- per-test pass/fail results with point values
- a final score out of 100
- a list of failed tests when applicable

## Notes
- The project uses a direct encoding style. Use the LEGv8 reference card for format layouts.
- I-format instructions are only `ADDI` and `SUBI`.
- Branch immediates are direct numeric offsets, not labels.
- The auto-grader is format-aware and scores the project using the weights above.
